import os
import shutil
import sys
import subprocess
import re
from datetime import datetime

# --- Determine Project Root Correctly --- START
# Check if running as a PyInstaller bundle
if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    # Running as executable: get the directory containing the executable
    PROJECT_ROOT = os.path.dirname(sys.executable)
    print(f"Running as executable, PROJECT_ROOT set to: {PROJECT_ROOT}")
else:
    # Running as a normal script: get the directory containing the script
    PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
    print(f"Running as script, PROJECT_ROOT set to: {PROJECT_ROOT}")
# --- Determine Project Root Correctly --- END

# Define paths relative to the determined project root
REPORTS_DIR = os.path.join(PROJECT_ROOT, 'reports')
OLD_FOLLOWERS_PATH = os.path.join(REPORTS_DIR, 'old_followers.json')
CURRENT_FOLLOWERS_1_PATH = os.path.join(REPORTS_DIR, 'followers_1.json')
CURRENT_FOLLOWING_PATH = os.path.join(REPORTS_DIR, 'following.json')
JSON_TRACKER_SCRIPT = os.path.join(PROJECT_ROOT, 'json_tracker.py')
JSON_HTTP_COMPARE_SCRIPT = os.path.join(PROJECT_ROOT, 'json_http_compare.py')

def find_latest_dated_folder(reports_path):
    """Finds the folder with the most recent YYYY.MM.DD name."""
    date_pattern = re.compile(r"^\d{4}\.\d{2}\.\d{2}$")
    latest_date = None
    latest_folder_path = None

    try:
        # Check if reports_path exists before listing directory
        if not os.path.isdir(reports_path):
             print(f"Error: Reports directory not found at {reports_path}")
             sys.exit(1)

        for item in os.listdir(reports_path):
            item_path = os.path.join(reports_path, item)
            if os.path.isdir(item_path) and date_pattern.match(item):
                try:
                    current_date = datetime.strptime(item, '%Y.%m.%d')
                    if latest_date is None or current_date > latest_date:
                        latest_date = current_date
                        latest_folder_path = item_path
                except ValueError:
                    # Ignore items that match pattern but aren't valid dates
                    continue
    except Exception as e: # Catch other potential OS errors
        print(f"Error accessing reports directory {reports_path}: {e}")
        sys.exit(1)

    if latest_folder_path:
        print(f"Found latest data folder: {os.path.basename(latest_folder_path)}")
        return latest_folder_path
    else:
        print(f"Error: No dated folders (YYYY.MM.DD) found in {reports_path}")
        sys.exit(1)

def run_script(script_path):
    """Runs a Python script using the same interpreter and handles errors."""
    if not os.path.exists(script_path):
        print(f"Error: Analysis script not found: {script_path}")
        return

    # Determine the Python executable to use
    # If running bundled, sys.executable is the app itself. We need python.
    # If not bundled, sys.executable is the python interpreter.
    python_executable = sys.executable
    # A simple heuristic: if running bundled, try to find 'python' or 'python3'
    # This is NOT foolproof, assumes python is in PATH relative to executable dir
    # or globally. A more robust solution might involve bundling python itself
    # or requiring it to be installed separately and in PATH.
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        # Try common names, preferring python3 if available
        found_python = False
        for name in ['python3', 'python']:
            try:
                # Check if the command exists and is executable
                test_cmd = [name, '--version']
                subprocess.run(test_cmd, check=True, capture_output=True, cwd=PROJECT_ROOT)
                python_executable = name
                print(f"Using '{python_executable}' to run analysis scripts.")
                found_python = True
                break
            except (FileNotFoundError, subprocess.CalledProcessError):
                continue
        if not found_python:
            print(f"Warning: Could not automatically find python/python3 executable.")
            print(f"         Analysis scripts ({os.path.basename(JSON_TRACKER_SCRIPT)}, {os.path.basename(JSON_HTTP_COMPARE_SCRIPT)}) might fail to run.")
            print(f"         Attempting to use sys.executable ({sys.executable}), which might be incorrect.")
            # Fallback to sys.executable, might be the bundled app itself
            # This will likely fail for the subprocess call below
            python_executable = sys.executable

    try:
        print(f"Running script: {os.path.basename(script_path)}...")
        # Use the determined python executable
        result = subprocess.run([python_executable, script_path], check=True, capture_output=True, text=True, cwd=PROJECT_ROOT)
        print(f"Output from {os.path.basename(script_path)}:")
        print(result.stdout)
        if result.stderr:
            print(f"Errors from {os.path.basename(script_path)}:")
            print(result.stderr)
        print(f"Finished running {os.path.basename(script_path)}.")
    except FileNotFoundError as e:
        print(f"Error: Interpreter '{python_executable}' or script '{script_path}' not found.")
        print(e)
    except subprocess.CalledProcessError as e:
        print(f"Error running script {os.path.basename(script_path)}:")
        print(e.stdout)
        print(e.stderr)

def main():
    """Automates updating Instagram follower data from the latest dated folder."""

    # --- 1. Find Latest Data Folder ---
    latest_data_folder = find_latest_dated_folder(REPORTS_DIR)

    # --- 2. Define Source File Paths ---
    source_followers_1 = os.path.join(latest_data_folder, 'followers_1.json')
    source_following = os.path.join(latest_data_folder, 'following.json')

    if not os.path.exists(source_followers_1):
        print(f"Error: Source file not found in latest folder: {source_followers_1}")
        sys.exit(1)
    if not os.path.exists(source_following):
        print(f"Error: Source file not found in latest folder: {source_following}")
        sys.exit(1)

    print("Source files located successfully in latest dated folder.")

    # --- 3. Manage root reports/ Files ---
    print("Managing files in root reports/ directory...")
    if os.path.exists(OLD_FOLLOWERS_PATH):
        try:
            os.remove(OLD_FOLLOWERS_PATH)
            print(f"- Deleted: {os.path.basename(OLD_FOLLOWERS_PATH)}")
        except OSError as e:
            print(f"Error deleting {OLD_FOLLOWERS_PATH}: {e}")
            sys.exit(1)

    if os.path.exists(CURRENT_FOLLOWING_PATH):
        try:
            os.remove(CURRENT_FOLLOWING_PATH)
            print(f"- Deleted: {os.path.basename(CURRENT_FOLLOWING_PATH)}")
        except OSError as e:
            print(f"Error deleting {CURRENT_FOLLOWING_PATH}: {e}")
            sys.exit(1)

    if os.path.exists(CURRENT_FOLLOWERS_1_PATH):
        try:
            os.rename(CURRENT_FOLLOWERS_1_PATH, OLD_FOLLOWERS_PATH)
            print(f"- Renamed: {os.path.basename(CURRENT_FOLLOWERS_1_PATH)} -> {os.path.basename(OLD_FOLLOWERS_PATH)}")
        except OSError as e:
            print(f"Error renaming {CURRENT_FOLLOWERS_1_PATH} to {OLD_FOLLOWERS_PATH}: {e}")
            sys.exit(1)
    else:
        print(f"- {os.path.basename(CURRENT_FOLLOWERS_1_PATH)} not found. Will copy new followers_1 without creating old_followers.")

    # --- 4. Copy New Files from Latest Folder to root reports/ ---
    print(f"Copying new files from {os.path.basename(latest_data_folder)} to root reports/...")
    try:
        shutil.copy2(source_followers_1, CURRENT_FOLLOWERS_1_PATH)
        print(f"- Copied {os.path.basename(source_followers_1)} to {REPORTS_DIR}")
        shutil.copy2(source_following, CURRENT_FOLLOWING_PATH)
        print(f"- Copied {os.path.basename(source_following)} to {REPORTS_DIR}")
    except Exception as e:
        print(f"Error copying files: {e}")
        sys.exit(1)

    # --- 5. Run Analysis Scripts ---
    print("\nRunning analysis scripts...")
    run_script(JSON_TRACKER_SCRIPT)
    run_script(JSON_HTTP_COMPARE_SCRIPT)

    print("\nInstagram data update process completed successfully!")

if __name__ == "__main__":
    main() 