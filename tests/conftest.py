import sys
from pathlib import Path

# 确保运行 pytest 时可以直接导入 src 包
ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))
