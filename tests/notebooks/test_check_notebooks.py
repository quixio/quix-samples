import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "utils"))
from check_notebooks import check  # noqa: E402

REPO = Path(__file__).resolve().parents[2]


def make(root: Path, extra=None, files=None):
    d = root / "python" / "notebooks" / "x"
    d.mkdir(parents=True)
    lib = {"libraryItemId": "x", "name": "X", "tags": {"Type": ["Notebook"]}, **(extra or {})}
    (d / "library.json").write_text(json.dumps(lib))
    for name, text in (files or {"x.py": "print(1)"}).items():
        (d / name).write_text(text)


class CheckNotebooks(unittest.TestCase):
    def run_case(self, **kw):
        with tempfile.TemporaryDirectory() as t:
            make(Path(t), **kw)
            return check(Path(t))

    def test_good_item_passes(self):
        self.assertEqual(self.run_case(), [])

    def test_deploy_settings_fails(self):
        self.assertTrue(self.run_case(extra={"DeploySettings": {}}))

    def test_variables_fails(self):
        self.assertTrue(self.run_case(extra={"Variables": []}))

    def test_two_py_files_fails(self):
        self.assertTrue(self.run_case(files={"a.py": "1", "b.py": "2"}))

    def test_token_placeholder_fails(self):
        self.assertTrue(self.run_case(files={"x.py": "t = '{placeholder:token}'"}))

    def test_real_repo_passes(self):
        self.assertEqual(check(REPO), [])


if __name__ == "__main__":
    unittest.main()
