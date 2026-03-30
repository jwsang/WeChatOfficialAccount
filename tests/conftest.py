import os
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
TEST_DB = ROOT_DIR / "data" / "test.db"
if TEST_DB.exists():
    TEST_DB.unlink()

os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DB.as_posix()}"

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))
