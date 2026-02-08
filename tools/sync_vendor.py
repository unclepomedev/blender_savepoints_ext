import shutil
import subprocess
from pathlib import Path

REPO_URL = "https://github.com/unclepomedev/blender_savepoints.git"
TARGET_FOLDER = "savepoints"
VENDOR_DIR = Path("vendor")
TEMP_DIR = Path("temp_clone")


def run_git(args, cwd=None):
    subprocess.run(["git"] + args, check=True, cwd=cwd)


def main():
    if not VENDOR_DIR.exists():
        VENDOR_DIR.mkdir()

    if TEMP_DIR.exists():
        shutil.rmtree(TEMP_DIR)

    print(f"🚀 Cloning '{TARGET_FOLDER}' from {REPO_URL}...")

    try:
        run_git(
            ["clone", "--depth", "1", "--filter=blob:none", "--sparse", REPO_URL, str(TEMP_DIR)]
        )

        run_git(["sparse-checkout", "set", TARGET_FOLDER], cwd=TEMP_DIR)

        dest_path = VENDOR_DIR / TARGET_FOLDER
        if dest_path.exists():
            print("🗑️ Removing old version...")
            shutil.rmtree(dest_path)

        src_path = TEMP_DIR / TARGET_FOLDER
        shutil.move(str(src_path), str(VENDOR_DIR))
        manifest_path = dest_path / "blender_manifest.toml"
        if manifest_path.exists():
            print(f"🗑️ Removing manifest file: {manifest_path}")
            manifest_path.unlink()

        print("✅ Vendor sync complete!")

    finally:
        if TEMP_DIR.exists():
            shutil.rmtree(TEMP_DIR, ignore_errors=True)


if __name__ == "__main__":
    main()
