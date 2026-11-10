import keyword
import re
import sys
from pathlib import Path

pipeline = "{{ cookiecutter.pipeline }}"

if not re.fullmatch(r"[a-z][a-z0-9_]*", pipeline) or keyword.iskeyword(pipeline):
    sys.exit(f"Invalid pipeline name '{pipeline}': use snake_case and avoid Python keywords.")

if re.search(r'["\\\n]', """{{ cookiecutter.owner | replace('"', '\\"') }}""".replace('\\"', '"')):
    sys.exit("Invalid owner: quotes and backslashes are not allowed.")

for path in (Path("core/pipelines") / pipeline, Path("migrations") / pipeline, Path("dags") / f"etl_{pipeline}.py"):
    if path.exists():
        sys.exit(f"{path} already exists.")
