import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parent
SCRIPTS = WORKSPACE.parent / 'scripts'
sys.path.insert(0, str(SCRIPTS))


@unittest.skipUnless(shutil.which('git'), 'Git is required for pin tests')
class GitPinTests(unittest.TestCase):
    def setUp(self):
        # Tests never create fixtures outside this sprint workspace.
        temp = tempfile.TemporaryDirectory(dir=WORKSPACE)
        self.addCleanup(temp.cleanup)
        self.repo = Path(temp.name)
        self.git('init', '-q')
        (self.repo / 'source.txt').write_text('source\n', encoding='utf-8')
        self.git('add', 'source.txt')
        self.git('commit', '-qm', 'fixture')
        self.pin = self.git('rev-parse', 'HEAD')
        self.git('tag', '-a', 'v0.23.4', '-m', 'annotated fixture tag')

    def git(self, *args):
        return subprocess.check_output(
            ['git', '-c', 'core.hooksPath=/dev/null', *args], cwd=self.repo, text=True,
            env={'PATH': os.environ['PATH'], 'GIT_CONFIG_NOSYSTEM': '1',
                 'GIT_CONFIG_GLOBAL': '/dev/null', 'GIT_AUTHOR_NAME': 'test',
                 'GIT_AUTHOR_EMAIL': 'fixture@invalid', 'GIT_COMMITTER_NAME': 'test',
                 'GIT_COMMITTER_EMAIL': 'fixture@invalid'},
        ).strip()

    def test_accepts_clean_exact_head_and_annotated_tag(self):
        from preflight import verify_upstream
        self.assertEqual(verify_upstream(self.repo, self.pin), self.pin)

    def test_rejects_different_head(self):
        from preflight import Blocker, verify_upstream
        self.git('commit', '--allow-empty', '-qm', 'second')
        with self.assertRaisesRegex(Blocker, 'HEAD.*expected'):
            verify_upstream(self.repo, self.pin)

    def test_rejects_tag_that_does_not_resolve_to_pin(self):
        from preflight import Blocker, verify_upstream
        self.git('tag', '-f', 'v0.23.4', 'HEAD^{tree}')
        with self.assertRaisesRegex(Blocker, 'refs/tags/v0.23.4'):
            verify_upstream(self.repo, self.pin)

    def test_rejects_checkout_subdirectory(self):
        from preflight import Blocker, verify_upstream
        nested = self.repo / 'nested'
        nested.mkdir()
        with self.assertRaisesRegex(Blocker, 'checkout root'):
            verify_upstream(nested, self.pin)

    def test_rejects_assume_unchanged(self):
        from preflight import Blocker, verify_upstream
        self.git('update-index', '--assume-unchanged', 'source.txt')
        (self.repo / 'source.txt').write_text('hidden edit\n', encoding='utf-8')
        with self.assertRaisesRegex(Blocker, 'assume-unchanged'):
            verify_upstream(self.repo, self.pin)

    def test_rejects_skip_worktree(self):
        from preflight import Blocker, verify_upstream
        self.git('update-index', '--skip-worktree', 'source.txt')
        (self.repo / 'source.txt').write_text('hidden edit\n', encoding='utf-8')
        with self.assertRaisesRegex(Blocker, 'skip-worktree'):
            verify_upstream(self.repo, self.pin)

    def test_rejects_dirty_checkout(self):
        from preflight import Blocker, verify_upstream
        (self.repo / 'source.txt').write_text('modified\n', encoding='utf-8')
        with self.assertRaisesRegex(Blocker, 'not clean'):
            verify_upstream(self.repo, self.pin)


class CLITests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(dir=WORKSPACE)
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)

    def executable(self, name, body):
        path = self.root / name
        path.write_text('#!/bin/sh\n' + body + '\n', encoding='utf-8')
        path.chmod(0o700)

    def run_preflight(self, *args):
        return subprocess.run(
            [sys.executable, '-B', str(SCRIPTS / 'preflight.py'),
             '--upstream', str(self.root / 'absent'), *args], cwd=self.root,
            env={'PATH': str(self.root)}, capture_output=True, text=True, timeout=20,
        )

    def test_version_probes_accept_exact_local_tools_without_project_context(self):
        self.executable('node', 'test "$1" = --version && test "$PWD" = / && printf "v26.12.1\\n"')
        self.executable('pnpm', '\n'.join([
            'test "$1" = --version && test "$PWD" = / &&',
            'test "$COREPACK_ENABLE_NETWORK" = 0 &&',
            'test "$npm_config_offline" = true &&',
            'test "$npm_config_manage_package_manager_versions" = false &&',
            'printf "12.15.0\\n"',
        ]))
        result = self.run_preflight()
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn('OK Node v26.12.1', result.stdout)
        self.assertIn('OK pnpm 12.15.0', result.stdout)
        self.assertIn('BLOCKER upstream', result.stdout)

    def test_reports_version_mismatches_together(self):
        self.executable('node', 'printf "v26.12.1-rc.1\\n"')
        self.executable('pnpm', 'printf "12.15.1\\n"')
        result = self.run_preflight()
        self.assertEqual(result.returncode, 1)
        self.assertIn('found v26.12.1-rc.1; expected v26.12.1', result.stdout)
        self.assertIn('found 12.15.1; expected 12.15.0', result.stdout)

    def test_reports_missing_tools(self):
        result = self.run_preflight()
        self.assertEqual(result.returncode, 1)
        self.assertIn('BLOCKER Node: node not found', result.stdout)
        self.assertIn('BLOCKER pnpm: pnpm not found', result.stdout)

    def test_prepared_receipt_inventory_is_printed_even_if_toolchain_is_blocked(self):
        app = self.root / 'app'
        prepared_fixture(app)
        result = self.run_preflight('--prepared-desktop', str(app))
        self.assertEqual(result.returncode, 1)
        self.assertIn('OK Desktop receipt', result.stdout)
        expected = hashlib.sha256(b'<html></html>\n').hexdigest()
        self.assertIn(f'{expected}  dist/index.html', result.stdout)


def prepared_fixture(app):
    files = {
        'package.json': b'{"main":"dist/electron-main.mjs"}\n',
        'dist/hermes-build.json': json.dumps({
            'schema': 1, 'product': 'desktop', 'outputHash': '0' * 64,
        }).encode('utf-8'),
        'dist/electron-main.mjs': b'// main\n',
        'dist/electron-preload.js': b'// preload\n',
        'dist/preview-guest-preload.js': b'// guest\n',
        'dist/index.html': b'<html></html>\n',
    }
    (app / 'dist').mkdir(parents=True)
    for name, contents in files.items():
        (app / name).write_bytes(contents)
    return files


class ReceiptTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(dir=WORKSPACE)
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.app = self.root / 'app'
        self.files = prepared_fixture(self.app)

    def test_hashes_all_six_required_files_in_path_order(self):
        from preflight import verify_desktop
        expected = [(name, hashlib.sha256(self.files[name]).hexdigest()) for name in sorted(self.files)]
        self.assertEqual(verify_desktop(self.app), expected)

    def test_rejects_malformed_json_with_desktop_text(self):
        from preflight import Blocker, verify_desktop
        (self.app / 'dist/hermes-build.json').write_bytes(b'start {"product":"desktop"}')
        with self.assertRaisesRegex(Blocker, r'hermes-build\.json.*JSON'):
            verify_desktop(self.app)

    def test_rejects_webapp_even_with_nested_desktop_marker(self):
        from preflight import Blocker, verify_desktop
        (self.app / 'dist/hermes-build.json').write_bytes(
            b'{"schema":1,"product":"webapp","nested":{"product":"desktop"}}')
        with self.assertRaisesRegex(Blocker, r'product.*desktop.*Webapp'):
            verify_desktop(self.app)

    def test_rejects_duplicate_json_keys(self):
        from preflight import Blocker, verify_desktop
        (self.app / 'dist/hermes-build.json').write_bytes(
            b'{"schema":1,"product":"webapp","product":"desktop"}')
        with self.assertRaisesRegex(Blocker, 'duplicate JSON key'):
            verify_desktop(self.app)

    def test_rejects_wrong_schema_and_invalid_output_hash(self):
        from preflight import Blocker, verify_desktop
        receipt = self.app / 'dist/hermes-build.json'
        for schema, digest, reason in [(True, '0' * 64, 'schema'), (1, 'not-a-digest', 'outputHash')]:
            with self.subTest(reason=reason):
                receipt.write_text(json.dumps({'schema': schema, 'product': 'desktop', 'outputHash': digest}),
                                   encoding='utf-8')
                with self.assertRaisesRegex(Blocker, reason):
                    verify_desktop(self.app)

    def test_rejects_wrong_package_entry(self):
        from preflight import Blocker, verify_desktop
        (self.app / 'package.json').write_bytes(b'{"main":"electron.js","nested":{"main":"dist/electron-main.mjs"}}')
        with self.assertRaisesRegex(Blocker, r'package\.json.*main.*dist/electron-main'):
            verify_desktop(self.app)

    def test_rejects_missing_nonregular_and_linked_required_file(self):
        from preflight import Blocker, verify_desktop
        path = self.app / 'dist/preview-guest-preload.js'
        path.unlink()
        for kind in ['missing', 'FIFO', 'symlink']:
            with self.subTest(kind=kind):
                if kind == 'FIFO':
                    os.mkfifo(path)
                if kind == 'symlink':
                    path.symlink_to('electron-preload.js')
                with self.assertRaisesRegex(Blocker, r'preview-guest-preload\.js.*regular file'):
                    verify_desktop(self.app)
                if kind != 'missing':
                    path.unlink()

    def test_rejects_linked_dist_directory(self):
        from preflight import Blocker, verify_desktop
        dist = self.app / 'dist'
        dist.rename(self.root / 'real-dist')
        dist.symlink_to(self.root / 'real-dist', target_is_directory=True)
        with self.assertRaisesRegex(Blocker, 'dist.*directory'):
            verify_desktop(self.app)

    def test_rejects_upstream_stale_marker(self):
        from preflight import Blocker, verify_desktop
        (self.app / 'dist/.hermes-stale').touch()
        with self.assertRaisesRegex(Blocker, r'\.hermes-stale'):
            verify_desktop(self.app)
