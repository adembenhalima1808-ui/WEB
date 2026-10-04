"""Build data/resume.txt (for the AI agent) and data/resume.pdf (public CV download) from resume.yaml.
The running site does this by itself whenever resume.yaml changes; this script is for a manual rebuild.
The phone number is deliberately left out of both outputs."""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from app.resume_build import build  # noqa: E402

build(pathlib.Path(__file__).parent / "resume.yaml", ROOT / "data")
print("ok")
