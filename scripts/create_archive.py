"""Create a clean ZIP archive of the entire KnightScope project."""

import os
import zipfile

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
zip_path = os.path.join(PROJECT_ROOT, "KnightScope_Deliverables.zip")

EXCLUDE_DIRS = {"__pycache__", ".pytest_cache", ".git", ".venv", "env", "node_modules"}
EXCLUDE_EXTS = {".pyc", ".pyo", ".zip"}

with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
    for root, dirs, files in os.walk(PROJECT_ROOT):
        # Filter directories in-place
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS and not d.startswith(".")]

        for file in files:
            ext = os.path.splitext(file)[1].lower()
            if ext in EXCLUDE_EXTS:
                continue
            if file.startswith("."):
                continue

            full_path = os.path.join(root, file)
            rel_path = os.path.relpath(full_path, PROJECT_ROOT)
            zipf.write(full_path, arcname=os.path.join("KnightScope", rel_path))

print(f"Project ZIP archive created successfully: {zip_path} ({os.path.getsize(zip_path) / 1024:.1f} KB)")
