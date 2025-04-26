import os
import subprocess
import sys
import shutil

SCRIPT_TO_PACKAGE = 'update_instagram_data.py'
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
DIST_DIR = os.path.join(PROJECT_ROOT, 'dist')
EXECUTABLE_NAME = os.path.splitext(SCRIPT_TO_PACKAGE)[0] # Name without .py

def check_pyinstaller():
    """Checks if PyInstaller is installed."""
    try:
        subprocess.run([sys.executable, '-m', 'PyInstaller', '--version'], check=True, capture_output=True)
        print("PyInstaller found.")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Error: PyInstaller is not installed or not found in PATH.")
        print("Please install it using: pip install pyinstaller")
        return False

def run_pyinstaller():
    """Runs the PyInstaller command."""
    print(f"\nRunning PyInstaller for {SCRIPT_TO_PACKAGE}...")
    command = [
        sys.executable,
        '-m',
        'PyInstaller',
        '--onefile', # Create a single executable file
        '--noconfirm', # Overwrite previous builds without asking
        SCRIPT_TO_PACKAGE
    ]
    try:
        # Run from project root to ensure paths are correct
        process = subprocess.run(command, cwd=PROJECT_ROOT, check=True, capture_output=True, text=True)
        print("PyInstaller finished successfully.")
        print("Output:")
        print(process.stdout)
        if process.stderr:
            print("Errors/Warnings:")
            print(process.stderr)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error running PyInstaller:")
        print(e.stdout)
        print(e.stderr)
        return False
    except FileNotFoundError:
        print(f"Error: Could not find {SCRIPT_TO_PACKAGE}.")
        return False

def move_executable():
    """Moves the executable from dist/ to the project root."""
    src_path_unix = os.path.join(DIST_DIR, EXECUTABLE_NAME) # Typical name on Unix-like systems
    src_path_win = os.path.join(DIST_DIR, f"{EXECUTABLE_NAME}.exe") # Typical name on Windows
    dest_path = os.path.join(PROJECT_ROOT, EXECUTABLE_NAME + ('.exe' if sys.platform == 'win32' else ''))

    executable_found = False
    src_path = None
    if os.path.exists(src_path_unix):
        src_path = src_path_unix
        executable_found = True
    elif os.path.exists(src_path_win):
        src_path = src_path_win
        executable_found = True

    if executable_found:
        print(f"\nMoving executable from {src_path} to {dest_path}...")
        try:
            shutil.move(src_path, dest_path)
            print(f"Executable successfully moved to project root: {os.path.basename(dest_path)}")
            # Optional: Clean up dist and build folders
            print("Cleaning up build artifacts (dist/, build/, *.spec)...")
            shutil.rmtree(DIST_DIR, ignore_errors=True)
            shutil.rmtree(os.path.join(PROJECT_ROOT, 'build'), ignore_errors=True)
            spec_file = os.path.join(PROJECT_ROOT, f"{EXECUTABLE_NAME}.spec")
            if os.path.exists(spec_file):
                os.remove(spec_file)
            print("Cleanup complete.")

        except Exception as e:
            print(f"Error moving executable or cleaning up: {e}")
    else:
        print(f"Error: Could not find the executable in {DIST_DIR} to move it.")

if __name__ == "__main__":
    if check_pyinstaller():
        if run_pyinstaller():
            move_executable()
    print("\nBuild script finished.") 