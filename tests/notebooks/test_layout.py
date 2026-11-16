import ast
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
# QuixLab draws a header and a code bar above the output. Keep room for both.
CHROME = 80
MIN_OUTPUT = 60
MAX_HEIGHT = 1100


def boxes(path):
    out = []
    for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
        for dec in getattr(node, "decorator_list", []):
            if isinstance(dec, ast.Call) and getattr(dec.func, "attr", "") in ("cell", "dataset"):
                kw = {k.arg: ast.literal_eval(k.value) for k in dec.keywords if k.arg != "viz"}
                (x, y), (w, h) = kw["position"], kw["size"]
                out.append((node.name, x, y, w, max(h, 150), kw.get("code_height", 200)))
    return out


class Layout(unittest.TestCase):
    def test_no_overlap_and_room_for_output(self):
        files = sorted((REPO / "python" / "notebooks").glob("*/*.py"))
        self.assertTrue(files)
        for f in files:
            bs = boxes(f)
            for i, a in enumerate(bs):
                self.assertGreaterEqual(a[4] - CHROME - a[5], MIN_OUTPUT, f"{f.name}: {a[0]} has no room for output")
                self.assertLessEqual(a[2] + a[4], MAX_HEIGHT, f"{f.name}: {a[0]} is too low")
                for b in bs[i + 1:]:
                    apart = a[1] + a[3] <= b[1] or b[1] + b[3] <= a[1] or a[2] + a[4] <= b[2] or b[2] + b[4] <= a[2]
                    self.assertTrue(apart, f"{f.name}: {a[0]} overlaps {b[0]}")


if __name__ == "__main__":
    unittest.main()
