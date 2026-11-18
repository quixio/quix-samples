#!/usr/bin/env python3
"""Audit hashed CA directories from an image without starting its container.

Docker archives are resolved in memory. Container symlinks are never followed
against the host filesystem. This checks stored anchors, not native clients.
"""
import argparse
import io
import json
from pathlib import Path
import posixpath
import re
import subprocess
import tarfile
import tempfile
from types import SimpleNamespace

import chain_check
import check_image


def ca_directories(configured):
    directories = []
    for path in ['/etc/ssl/certs', '/etc/pki/tls/certs', *configured.split(':')]:
        if not path:
            continue
        if not path.startswith('/') or '\n' in path or '\x00' in path:
            raise chain_check.EvidenceError('CA directories must be absolute')
        # Linux treats repeated leading slashes as one; posixpath alone retains //.
        normalized = posixpath.normpath('/' + path.lstrip('/'))
        if normalized == '/':
            raise chain_check.EvidenceError('The filesystem root is not a supported CA directory')
        if normalized not in directories:
            directories.append(normalized)
    return directories


def add_archive(files, prefix, data):
    with tarfile.open(fileobj=io.BytesIO(data)) as archive:
        for member in archive:
            name = posixpath.normpath(member.name)
            if name.startswith('/') or name == '..' or name.startswith('../'):
                raise chain_check.EvidenceError('Unsafe archive member path')
            path = posixpath.normpath(prefix + '/' + name)
            if member.isfile():
                files[path] = ('file', archive.extractfile(member).read())
            elif member.issym():
                target = member.linkname
                files[path] = ('link', posixpath.normpath(target if target.startswith('/')
                              else posixpath.dirname(path) + '/' + target))
            elif member.islnk():
                files[path] = ('link', posixpath.normpath(prefix + '/' + member.linkname))


def resolve(files, path, seen=None):
    seen = set() if seen is None else seen
    if path in seen:
        raise chain_check.EvidenceError('Cycle in container CA symlinks')
    seen.add(path)
    if path not in files:
        raise chain_check.EvidenceError('Unresolved container CA target: ' + path)
    kind, value = files[path]
    return value if kind == 'file' else resolve(files, value, seen)


def validate_extraction_container(inspected, identifier, image_id):
    if (not re.fullmatch(r'[a-f0-9]{64}', identifier)
            or not isinstance(inspected, list) or len(inspected) != 1
            or not isinstance(inspected[0], dict)):
        raise chain_check.EvidenceError('Invalid extraction container inspection')
    container = inspected[0]
    if container.get('Id') != identifier or container.get('Image') != image_id:
        raise chain_check.EvidenceError('Extraction container identity or image does not match')
    state = container.get('State')
    if (not isinstance(state, dict) or state.get('Status') != 'created'
            or state.get('Running') is not False
            or not re.fullmatch(r'0001-01-01T00:00:00(?:\.0+)?Z',
                                str(state.get('StartedAt', '')))):
        raise chain_check.EvidenceError('Extraction container must never have been started')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--image', required=True)
    parser.add_argument('--context', default='orbstack')
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--extraction-container',
                        help='Parent-owned, never-started container for the same image; never removed here')
    args = parser.parse_args()
    docker = ['docker', '--context', args.context]
    report = {'scope': 'static hashed CA directories only; container never started',
              'checks': [], 'errors': []}
    container = None
    owns_container = False
    try:
        inspected = check_image.execute(docker + ['image', 'inspect', args.image])
        report['image'] = check_image.image_evidence(json.loads(
            check_image.require_success(inspected, 'Inspect image')))
        if args.extraction_container:
            if not re.fullmatch(r'[a-f0-9]{64}', args.extraction_container):
                raise chain_check.EvidenceError('Extraction container requires its full container ID')
            inspected_container = check_image.execute(
                docker + ['container', 'inspect', args.extraction_container])
            validate_extraction_container(json.loads(check_image.require_success(
                inspected_container, 'Inspect extraction container')),
                args.extraction_container, report['image']['id'])
            container = args.extraction_container
        else:
            created = check_image.execute(docker + ['create', '--pull=never', '--platform',
                'linux/amd64', '--label', 'quixwork=static-ca-directories', '--entrypoint',
                '/bin/true', report['image']['id']])
            container = check_image.require_success(created, 'Create extraction container').strip()
            if not re.fullmatch(r'[a-f0-9]{64}', container):
                container = None
                raise chain_check.EvidenceError('Invalid container ID')
            owns_container = True
        report['extraction_container'] = {
            'id': container, 'owned_by': 'checker' if owns_container else 'parent',
            'container_started': False,
        }
        configured = report['image']['trust_environment'].get('SSL_CERT_DIR', '')
        directories = ca_directories(configured)
        roots = list(dict.fromkeys(directories + ['/usr/share/ca-certificates',
            '/usr/local/share/ca-certificates', '/etc/pki/ca-trust/extracted']))
        files = {}
        report['absent_directories'] = []
        for root in roots:
            copied = subprocess.run(docker + ['cp', container + ':' + root + '/.', '-'],
                                    capture_output=True, timeout=30)
            if copied.returncode:
                error = copied.stderr.decode(errors='replace')
                if re.search(r'could not find the file|no such file or directory', error, re.I):
                    report['absent_directories'].append(root)
                    continue
                raise chain_check.EvidenceError('Cannot archive CA directory ' + root)
            add_archive(files, root, copied.stdout)
        openssl, report['openssl'] = check_image.select_openssl(None)
        check_args = SimpleNamespace(openssl=openssl,
                                     fixtures_dir=Path(__file__).parent / 'fixtures')
        control = chain_check.load_fixtures(check_args.fixtures_dir, openssl)
        with tempfile.TemporaryDirectory(prefix='quix-static-ca-') as temporary:
            temporary = Path(temporary)
            positive = temporary / 'published-roots.pem'
            positive.write_text(control)
            if chain_check.check_store(check_args, positive)['accepted'] != 12:
                raise chain_check.EvidenceError('Fixture positive control failed')
            report['positive_control'] = '12/12 accepted'
            for index, root in enumerate(directories):
                destination = temporary / str(index)
                destination.mkdir()
                entries = [p for p in files if posixpath.dirname(p) == root
                           and re.fullmatch(r'[a-f0-9]{8}\.\d+', posixpath.basename(p))]
                for path in entries:
                    (destination / posixpath.basename(path)).write_bytes(resolve(files, path))
                if entries:
                    result = chain_check.check_store(check_args, destination, directory=True)
                    result['path'] = root
                else:
                    result = {'path': root, 'status': 'no_hashed_anchors', 'hashed_entries': 0}
                report['checks'].append(result)
    except (chain_check.EvidenceError, OSError, ValueError, tarfile.TarError,
            subprocess.TimeoutExpired) as error:
        report['errors'].append(str(error))
    finally:
        if container and owns_container:
            try:
                removed = check_image.execute(docker + ['rm', '--force', '--volumes', container])
                check_image.require_success(removed, 'Remove own extraction container')
            except chain_check.EvidenceError as error:
                report['errors'].append(str(error))
    exposed = any(row.get('accepted', 0) for row in report['checks'])
    code = 2 if report['errors'] else 1 if exposed else 0
    report['status'] = 'error' if code == 2 else 'exposed' if code == 1 else 'passed_selected_checks'
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({'image': args.image, 'status': report['status'], 'output': str(args.output)}))
    return code


if __name__ == '__main__':
    raise SystemExit(main())
