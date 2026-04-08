import subprocess
import sys
import os
import time
import tkinter as tk
from tkinter import filedialog
from pywinauto import Application, Desktop
from pywinauto.keyboard import send_keys

CAMTASIA_PATH = r"C:\Program Files\TechSmith\Camtasia 2025\CamtasiaStudio.exe"


def select_media_files():
    """Show a dialog for the user to select media files to import."""
    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)

    files = filedialog.askopenfilenames(
        title="Select Media Files to Import",
        filetypes=[
            ("Media files", "*.mp4 *.avi *.mov *.wmv *.mkv *.mp3 *.wav *.png *.jpg *.jpeg *.gif *.bmp *.trec"),
            ("Video files", "*.mp4 *.avi *.mov *.wmv *.mkv *.trec"),
            ("Audio files", "*.mp3 *.wav"),
            ("Image files", "*.png *.jpg *.jpeg *.gif *.bmp"),
            ("All files", "*.*"),
        ],
    )

    root.destroy()

    if not files:
        print("No files selected. Exiting.")
        sys.exit(0)

    print(f"Selected {len(files)} file(s):")
    for f in files:
        print(f"  {f}")
    return list(files)


def launch_camtasia():
    if not os.path.exists(CAMTASIA_PATH):
        print(f"Error: Camtasia not found at:\n  {CAMTASIA_PATH}")
        sys.exit(1)

    # Step 1: Ask user to select media files
    media_files = select_media_files()

    # Step 2: Launch Camtasia
    print("Starting Camtasia 2025...")
    subprocess.Popen([CAMTASIA_PATH])

    # Wait for Camtasia window to appear
    print("Waiting for Camtasia to load...")
    app = None
    for _ in range(30):
        time.sleep(2)
        try:
            app = Application(backend="uia").connect(title="TechSmith Camtasia 2025")
            break
        except Exception:
            pass

    if not app:
        print("Camtasia window not found after waiting.")
        sys.exit(1)

    camtasia = app.window(title="TechSmith Camtasia 2025")
    print(f"Found window: '{camtasia.window_text()}'")

    # Dismiss crash recovery dialog if present
    try:
        discard_btn = camtasia.child_window(title="Discard", control_type="Button")
        if discard_btn.exists(timeout=3):
            print("Dismissing recovery dialog...")
            discard_btn.click()
            time.sleep(1)
    except:
        pass

    # Step 3: Click New Project
    print("Waiting for 'New Project' button...")
    try:
        new_proj_btn = camtasia.child_window(title="_New Project", control_type="Button", found_index=0)
        new_proj_btn.wait("visible", timeout=30)
        print("Clicking 'New Project'...")
        new_proj_btn.click_input()
    except Exception as e:
        print(f"Failed to click 'New Project': {e}")
        sys.exit(1)

    # Wait for the editor window to load
    print("Waiting for editor to load...")
    time.sleep(8)

    # The app object is still valid; find the editor window
    editor = None
    for _ in range(15):
        try:
            for w in Desktop(backend="uia").windows():
                title = w.window_text()
                if "Camtasia" in title:
                    pid = w.process_id()
                    app = Application(backend="uia").connect(process=pid)
                    editor = app.top_window()
                    break
        except Exception:
            pass
        if editor:
            break
        time.sleep(2)

    if not editor:
        print("Could not find Camtasia editor window.")
        sys.exit(1)

    print(f"Editor window: '{editor.window_text()}'")

    # Step 4: Import media via Ctrl+I
    print("Opening import dialog (Ctrl+I)...")
    editor.set_focus()
    time.sleep(1)
    send_keys("^i")
    time.sleep(2)

    # Wait for the file dialog to appear
    print("Waiting for file dialog...")
    open_dlg = None
    for _ in range(15):
        time.sleep(1)
        try:
            for w in Desktop(backend="uia").windows():
                title = w.window_text()
                ctype = w.element_info.control_type
                # Match only actual file dialogs (Dialog type with Open/Import in title)
                if ctype == "Window" and any(k in title for k in ["Open", "Import Media"]):
                    # Verify it has a "File name:" edit to confirm it's a file dialog
                    try:
                        w.child_window(title="File name:", control_type="Edit")
                        pid = w.process_id()
                        dlg_app = Application(backend="uia").connect(process=pid)
                        open_dlg = dlg_app.window(title=title)
                        break
                    except Exception:
                        pass
        except Exception:
            pass
        if open_dlg:
            break

    if not open_dlg:
        print("Could not find the import file dialog.")
        sys.exit(1)

    print(f"Found dialog: '{open_dlg.window_text()}'")

    # Type file paths into the filename box
    if len(media_files) == 1:
        file_string = media_files[0]
    else:
        file_string = " ".join(f'"{f}"' for f in media_files)

    try:
        edit = open_dlg.child_window(title="File name:", control_type="Edit")
        edit.set_text(file_string)
        time.sleep(1)

        open_btn = open_dlg.child_window(title="Open", control_type="Button")
        open_btn.click_input()
        print(f"Imported {len(media_files)} file(s). Done!")
    except Exception as e:
        print(f"Failed to import files: {e}")
        sys.exit(1)


if __name__ == "__main__":
    launch_camtasia()
