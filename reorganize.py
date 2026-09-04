#!/usr/bin/env python3
"""
Reorganize the LinkedIn automation repo into a multi-platform structure.

Run this from INSIDE the "Linkedin automation" project root (where main.py
currently lives). It only MOVES existing files into new folders — it does
NOT touch any import statements inside them. After running this, you must
manually fix imports in the moved files before anything will run again.

Recommended: run this, fix imports, test that LinkedIn still works, THEN
commit, THEN start adding telegram/publisher.py and discord/publisher.py.
"""

from pathlib import Path
import shutil

ROOT = Path(".")

# (source filename in root) -> (destination folder relative to root)
MOVES = {
    "publisher.py": "platforms/linkedin",
    "agent.py": "core",
    "content_gen.py": "core",
    "image_gen.py": "core",
    "tools.py": "core",
    "Architecture.png": "docs",
    "image.png": "docs",
    "linkedin_poster_editorial.png": "docs",
}

NEW_DIRS = [
    "core",
    "platforms",
    "platforms/linkedin",
    "platforms/telegram",
    "platforms/discord",
    "docs",
]

INIT_FILES = [
    "core/__init__.py",
    "platforms/__init__.py",
    "platforms/linkedin/__init__.py",
    "platforms/telegram/__init__.py",
    "platforms/discord/__init__.py",
]


def main() -> None:
    # 1. create all target directories
    for d in NEW_DIRS:
        (ROOT / d).mkdir(parents=True, exist_ok=True)
        print(f"created dir: {d}/")

    # 2. create __init__.py for every new package
    for f in INIT_FILES:
        path = ROOT / f
        path.touch(exist_ok=True)
        print(f"created: {f}")

    # 3. move each existing file into its new home, skipping anything
    #    that's already missing (so this script is safe to re-run)
    for filename, dest_folder in MOVES.items():
        src = ROOT / filename
        dest = ROOT / dest_folder / filename
        if not src.exists():
            print(f"SKIP (not found, already moved?): {filename}")
            continue
        if dest.exists():
            print(f"SKIP (destination already exists): {dest}")
            continue
        shutil.move(str(src), str(dest))
        print(f"moved: {filename} -> {dest_folder}/{filename}")

    print("\nDone moving files. NEXT STEPS (manual, do not skip):")
    print("1. Open main.py and every moved file — fix import statements")
    print("   to match the new paths, e.g.:")
    print("     from publisher import ...      ->  from platforms.linkedin.publisher import ...")
    print("     from content_gen import ...    ->  from core.content_gen import ...")
    print("2. Run your existing LinkedIn automation and confirm it still")
    print("   works exactly as before.")
    print("3. Only once that's confirmed working, add:")
    print("     platforms/telegram/publisher.py")
    print("     platforms/discord/publisher.py")


if __name__ == "__main__":
    main()