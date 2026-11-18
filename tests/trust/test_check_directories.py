import contextlib
import copy
import io
import json
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile
import unittest
from unittest.mock import patch

import check_directories
from check_directories import add_archive, ca_directories, resolve, validate_extraction_container
from chain_check import EvidenceError


class ContainerArchiveTests(unittest.TestCase):
    def test_configured_directory_aliases_are_normalized_before_deduplication(self):
        self.assertEqual(
            ca_directories('/custom/:/custom/./://custom///:/etc/ssl/certs/'),
            ['/etc/ssl/certs', '/etc/pki/tls/certs', '/custom'],
        )

    def test_relative_and_filesystem_root_directories_are_rejected(self):
        for path in ('relative', '/', '//', '///./', '/custom/..'):
            with self.subTest(path=path), self.assertRaises(EvidenceError):
                ca_directories(path)

    def test_absolute_container_symlink_resolves_only_in_virtual_filesystem(self):
        files = {'/etc/ssl/certs/abcd.0': ('link', '/usr/share/ca/root.crt'),
                 '/usr/share/ca/root.crt': ('file', b'certificate')}
        self.assertEqual(resolve(files, '/etc/ssl/certs/abcd.0'), b'certificate')

    def test_missing_target_does_not_fall_back_to_host_filesystem(self):
        with self.assertRaises(EvidenceError):
            resolve({'/ca': ('link', '/etc/passwd')}, '/ca')

    def test_symlink_cycle_fails(self):
        with self.assertRaises(EvidenceError):
            resolve({'/a': ('link', '/b'), '/b': ('link', '/a')}, '/a')

    def test_parent_archive_traversal_fails(self):
        data = io.BytesIO()
        with tarfile.open(fileobj=data, mode='w') as archive:
            entry = tarfile.TarInfo('../escape')
            archive.addfile(entry, io.BytesIO(b''))
        with self.assertRaises(EvidenceError):
            add_archive({}, '/etc/ssl/certs', data.getvalue())


class ExtractionContainerTests(unittest.TestCase):
    container_id = 'a' * 64
    image_id = 'sha256:' + 'b' * 64

    def inspection(self):
        return [{'Id': self.container_id, 'Image': self.image_id, 'State': {
            'Status': 'created', 'Running': False, 'StartedAt': '0001-01-01T00:00:00Z',
        }}]

    def test_matching_never_started_container_is_allowed(self):
        validate_extraction_container(self.inspection(), self.container_id, self.image_id)

    def test_wrong_container_or_image_is_rejected(self):
        for key, value in (('Id', 'c' * 64), ('Image', 'sha256:' + 'c' * 64)):
            with self.subTest(key=key):
                inspected = self.inspection()
                inspected[0][key] = value
                with self.assertRaisesRegex(EvidenceError, 'does not match'):
                    validate_extraction_container(inspected, self.container_id, self.image_id)

    def test_started_or_unknown_state_is_rejected(self):
        states = [None, {}, {'Status': 'running', 'Running': True, 'StartedAt': '2026-10-22T00:00:00Z'}]
        for key, value in (('Status', 'exited'), ('Running', True),
                           ('StartedAt', '2026-10-22T00:00:00Z')):
            state = copy.deepcopy(self.inspection()[0]['State'])
            state[key] = value
            states.append(state)
        for state in states:
            with self.subTest(state=state):
                inspected = self.inspection()
                inspected[0]['State'] = state
                with self.assertRaisesRegex(EvidenceError, 'never have been started'):
                    validate_extraction_container(inspected, self.container_id, self.image_id)

    def run_checker(self, external, archive_error=False):
        commands = []
        image = [{'Id': self.image_id, 'Os': 'linux', 'Architecture': 'amd64', 'Config': {}}]

        def execute(command):
            commands.append(command)
            if 'image' in command and 'inspect' in command:
                output = json.dumps(image)
            elif 'container' in command and 'inspect' in command:
                output = json.dumps(self.inspection())
            else:
                output = self.container_id
            return subprocess.CompletedProcess(command, 0, output, '')

        archived = subprocess.CompletedProcess([], 1, b'',
            b'Permission denied' if archive_error else b'Could not find the file')
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / 'report.json'
            arguments = ['check_directories.py', '--image', self.image_id, '--output', str(output)]
            if external:
                arguments.extend(['--extraction-container', self.container_id])
            with patch.object(sys, 'argv', arguments), \
                    patch('check_directories.check_image.execute', side_effect=execute), \
                    patch('check_directories.subprocess.run', return_value=archived), \
                    patch('check_directories.check_image.select_openssl', return_value=('openssl', 'mock')), \
                    patch('check_directories.chain_check.load_fixtures', return_value='roots'), \
                    patch('check_directories.chain_check.check_store', return_value={'accepted': 12}), \
                    contextlib.redirect_stdout(io.StringIO()):
                code = check_directories.main()
            return code, json.loads(output.read_text()), commands

    def test_parent_container_is_never_created_or_removed_by_helper(self):
        for failure in (False, True):
            with self.subTest(archive_error=failure):
                code, report, commands = self.run_checker(external=True, archive_error=failure)
                self.assertEqual(code, 2 if failure else 0)
                self.assertEqual(report['extraction_container']['owned_by'], 'parent')
                self.assertFalse(any('create' in command or 'rm' in command for command in commands))

    def test_standalone_container_is_removed_on_success_and_failure(self):
        for failure in (False, True):
            with self.subTest(archive_error=failure):
                code, report, commands = self.run_checker(external=False, archive_error=failure)
                self.assertEqual(code, 2 if failure else 0)
                self.assertEqual(report['extraction_container']['owned_by'], 'checker')
                self.assertEqual(sum('create' in command for command in commands), 1)
                self.assertEqual(sum('rm' in command for command in commands), 1)
                self.assertEqual(commands[-1][-1], self.container_id)


if __name__ == '__main__':
    unittest.main()
