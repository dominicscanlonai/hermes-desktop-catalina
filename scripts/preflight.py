#!/usr/bin/env python3
"""Read-only source preparation checks for the pinned Hermes Desktop checkout."""
import argparse
from contextlib import contextmanager
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import subprocess

UPSTREAM_COMMIT = '8fc0374447313e276f6b9a2764bfc750190c966a'
UPSTREAM_TAG = 'refs/tags/v0.23.4'
NODE_VERSION = '26.12.1'
PNPM_VERSION = '12.15.0'


class Blocker(Exception):
    """An unmet preflight requirement."""


def local_command(args, *, cwd, settings):
    # Don't inherit tool injection or repository-routing variables.
    env = {'PATH': os.environ.get('PATH', os.defpath), 'LC_ALL': 'C', **settings}
    try:
        result = subprocess.run(args, cwd=cwd, env=env, stdin=subprocess.DEVNULL,
                                capture_output=True, encoding='utf-8', errors='replace', timeout=15)
    except FileNotFoundError as exc:
        raise Blocker(f'{args[0]} not found or its interpreter is unavailable') from exc
    except subprocess.TimeoutExpired as exc:
        raise Blocker(f'{args[0]} timed out') from exc
    except OSError as exc:
        raise Blocker(f'could not run {args[0]}: {exc.strerror}') from exc
    if result.returncode:
        detail = result.stderr.splitlines()
        reason = f': {detail[0]}' if detail else ''
        raise Blocker(f'{" ".join(args)} exited {result.returncode}{reason}')
    return result.stdout.rstrip('\r\n')


def verify_upstream(root, pin=UPSTREAM_COMMIT):
    try:
        root = root.resolve(strict=True)
    except (OSError, RuntimeError) as exc:
        raise Blocker(f'upstream checkout is unavailable: {root}') from exc
    if not root.is_dir():
        raise Blocker(f'upstream checkout is not a directory: {root}')

    def git(*args):
        return local_command(
            ['git', '--no-replace-objects', '-c', 'core.fsmonitor=false', *args], cwd=root,
            settings={'GIT_OPTIONAL_LOCKS': '0', 'GIT_NO_LAZY_FETCH': '1',
                      'GIT_ALLOW_PROTOCOL': '', 'GIT_TERMINAL_PROMPT': '0',
                      'GIT_CONFIG_NOSYSTEM': '1', 'GIT_CONFIG_GLOBAL': '/dev/null'},
        )

    if Path(git('rev-parse', '--show-toplevel')).resolve() != root:
        raise Blocker(f'use the upstream checkout root, not a subdirectory: {root}')
    head = git('rev-parse', '--verify', 'HEAD^{commit}')
    if head != pin:
        raise Blocker(f'HEAD is {head}; expected {pin}')
    tag_commit = git('rev-parse', '--verify', f'{UPSTREAM_TAG}^{{commit}}')
    if tag_commit != pin:
        raise Blocker(f'{UPSTREAM_TAG} resolves to {tag_commit}; expected {pin}')
    # These index flags can hide working-tree edits from git status.
    tags = {entry[0] for entry in git('ls-files', '-v', '-z').split('\0') if entry}
    if tags & {'S', 's'}:
        raise Blocker('index contains skip-worktree entries; use a fresh full checkout')
    if any(tag.islower() for tag in tags):
        raise Blocker('index contains assume-unchanged entries; use a fresh full checkout')
    if git('status', '--porcelain=v1', '--untracked-files=normal', '--ignore-submodules=none'):
        raise Blocker('upstream checkout is not clean (tracked edits or untracked files)')
    return head


def verify_version(executable, expected):
    # Probe installed commands only, away from a workspace manifest. Corepack
    # and pnpm must not fetch or switch to a different package manager.
    found = local_command(
        [executable, '--version'], cwd='/',
        settings={'HOME': '/dev/null', 'COREPACK_ENABLE_NETWORK': '0',
                  'COREPACK_ENABLE_AUTO_PIN': '0', 'COREPACK_ENABLE_PROJECT_SPEC': '0',
                  'npm_config_userconfig': '/dev/null', 'npm_config_offline': 'true',
                  'npm_config_manage_package_manager_versions': 'false'},
    )
    if found != expected:
        raise Blocker(f'found {found or "(no version)"}; expected {expected}')
    return found


@contextmanager
def open_input(path, label, *, parent=None, directory=False):
    flags = os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK
    if directory:
        flags |= os.O_DIRECTORY
    kind = 'directory' if directory else 'regular file'
    try:
        fd = os.open(path, flags, dir_fd=parent)
        try:
            if not directory and not stat.S_ISREG(os.fstat(fd).st_mode):
                raise Blocker(f'{label}: expected a regular file, not a special file')
            if not directory and os.fstat(fd).st_size == 0:
                raise Blocker(f'{label}: file is empty')
            yield fd
        finally:
            os.close(fd)
    except OSError as exc:
        raise Blocker(f'{label}: expected a non-symlink {kind} ({exc.strerror})') from exc


def json_object(raw, label):
    def unique_pairs(pairs):
        obj = dict(pairs)
        if len(obj) != len(pairs):
            raise ValueError('duplicate JSON key')
        return obj

    def reject_constant(token):
        raise ValueError(f'not a JSON value: {token}')

    try:
        data = json.loads(raw.decode('utf-8'), object_pairs_hook=unique_pairs,
                          parse_constant=reject_constant)
    except (ValueError, RecursionError) as exc:
        raise Blocker(f'{label}: invalid JSON ({exc})') from exc
    if not isinstance(data, dict):
        raise Blocker(f'{label}: expected a JSON object')
    return data


def inventory_digest(stream, name):
    if name not in ('dist/hermes-build.json', 'package.json'):
        digest = hashlib.sha256()
        for chunk in iter(lambda: stream.read(256 * 1024), b''):
            digest.update(chunk)
        return digest.hexdigest()

    limit = 1024 * 1024
    raw = stream.read(limit + 1)
    if len(raw) > limit:
        raise Blocker(f'{name}: JSON exceeds 1 MiB')
    data = json_object(raw, name)
    if name == 'dist/hermes-build.json':
        if data.get('product') != 'desktop':
            raise Blocker(f'{name}: product must be desktop, not Webapp or another product')
        if type(data.get('schema')) is not int or data['schema'] != 1:
            raise Blocker(f'{name}: expected receipt schema 1')
        output_hash = data.get('outputHash')
        if not isinstance(output_hash, str) or not re.fullmatch('[0-9a-f]{64}', output_hash):
            raise Blocker(f'{name}: expected a SHA-256 outputHash field')
    elif data.get('main') != 'dist/electron-main.mjs':
        raise Blocker(f'{name}: main must be dist/electron-main.mjs')
    return hashlib.sha256(raw).hexdigest()


def verify_desktop(app):
    required = ('dist/hermes-build.json', 'package.json', 'dist/electron-main.mjs',
                'dist/electron-preload.js', 'dist/preview-guest-preload.js', 'dist/index.html')
    inventory = []
    with open_input(app, 'Desktop app root', directory=True) as root:
        with open_input('dist', 'dist', parent=root, directory=True) as dist:
            try:
                os.stat('.hermes-stale', dir_fd=dist, follow_symlinks=False)
            except FileNotFoundError:
                pass
            else:
                raise Blocker('dist/.hermes-stale is present; rebuild Desktop before using it')

            try:
                native = os.stat('node_modules', dir_fd=dist, follow_symlinks=False)
            except FileNotFoundError:
                pass
            else:
                if not stat.S_ISDIR(native.st_mode):
                    raise Blocker('dist/node_modules: expected a non-symlink directory')
            for name in required:
                parent, filename = (dist, name[5:]) if name.startswith('dist/') else (root, name)
                with open_input(filename, name, parent=parent) as fd:
                    with os.fdopen(fd, 'rb', closefd=False) as stream:
                        inventory.append((name, inventory_digest(stream, name)))
    return sorted(inventory)


def report_desktop(app):
    inventory = verify_desktop(app)
    print('OK Desktop receipt (schema and required files)')
    print('SHA-256 inventory (required files only):')
    for name, digest in inventory:
        print(f'{digest}  {name}')


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--upstream', type=Path, help='local upstream Git checkout root')
    mode.add_argument('--desktop-only', action='store_true', help='only parse and inventory an existing Desktop output')
    parser.add_argument('--prepared-desktop', type=Path,
                        help='also validate and inventory an existing apps/desktop directory')
    args = parser.parse_args(argv)
    if args.desktop_only and args.prepared_desktop is None:
        parser.error('--desktop-only requires --prepared-desktop')
    checks = [] if args.desktop_only else [
        ('upstream', lambda: f'{UPSTREAM_TAG} at {verify_upstream(args.upstream)} (clean)'),
        ('Node', lambda: verify_version('node', 'v' + NODE_VERSION)),
        ('pnpm', lambda: verify_version('pnpm', PNPM_VERSION)),
    ]
    blocked = False
    for name, check in checks:
        try:
            print(f'OK {name} {check()}')
        except Blocker as exc:
            blocked = True
            print(f'BLOCKER {name}: {exc}')
    if args.prepared_desktop is not None:
        try:
            report_desktop(args.prepared_desktop)
        except Blocker as exc:
            blocked = True
            print(f'BLOCKER Desktop receipt: {exc}')
    print('Preflight blocked; no build attempted.' if blocked else
          'Preflight passed; no build attempted.')
    return int(blocked)


if __name__ == '__main__':
    raise SystemExit(main())
