"""Keep the Dockerfiles, reviewed base-image lock and trust inventory aligned."""
import json
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[2]


class BasePinsTest(unittest.TestCase):
    def test_all_catalog_stages_match_reviewed_pins(self):
        lock = json.loads((ROOT / 'tests/trust/base-images.lock.json').read_text())
        catalog = json.loads((ROOT / 'tests/trust/catalog.json').read_text())
        used = set()
        for entry in catalog['dockerfiles']:
            text = (ROOT / entry['path']).read_text()
            bases = re.findall(r'^FROM\s+(\S+)', text, re.M | re.I)
            self.assertEqual(bases, [s['base'] for s in entry['candidate_stages']], entry['path'])
            if entry['path'] in lock['unqualified_unpinned']:
                continue
            for base in bases:
                name, separator, digest = base.partition('@')
                self.assertEqual(separator, '@', entry['path'])
                self.assertRegex(digest, r'^sha256:[a-f0-9]{64}$')
                self.assertEqual(digest, lock['images'][name]['digest'], entry['path'])
                self.assertTrue(lock['images'][name]['evidence'])
                used.add(name)
        self.assertEqual(used, set(lock['images']))
        actual = {str(p.relative_to(ROOT)) for p in ROOT.rglob('*')
                  if p.is_file() and p.name.lower().startswith('dockerfile') and '.git' not in p.parts}
        self.assertEqual(actual, {d['path'] for d in catalog['dockerfiles']})
