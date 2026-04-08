from pywinauto import Desktop
import subprocess, time, os

CAMTASIA_PATH = r"C:\Program Files\TechSmith\Camtasia 2025\CamtasiaStudio.exe"

print("Launching Camtasia...")
subprocess.Popen([CAMTASIA_PATH])

# Wait and poll for new windows
for i in range(30):
    time.sleep(2)
    print(f"\n--- Poll {i+1} ---")
    desktop = Desktop(backend="uia")
    windows = desktop.windows()
    for w in windows:
        try:
            title = w.window_text()
            if title.strip():
                print(f"  '{title}'")
        except:
            pass
    # Check if any new interesting window appeared
    for w in windows:
        try:
            title = w.window_text()
            # Look for anything related to Camtasia/TechSmith or a home/welcome screen
            keywords = ["camtasia", "techsmith", "new project", "home", "welcome", "recorder"]
            if any(k in title.lower() for k in keywords):
                print(f"\n*** FOUND: '{title}' ***")
                def dump(ctrl, depth=0):
                    if depth > 3:
                        return
                    try:
                        indent = "  " * depth
                        ctype = ctrl.element_info.control_type
                        txt = ctrl.window_text()
                        cls = ctrl.friendly_class_name()
                        print(f"{indent}{cls} | '{txt}' | type={ctype}")
                    except:
                        pass
                    if depth < 3:
                        for c in ctrl.children():
                            dump(c, depth + 1)
                dump(w)
                print("*** END DUMP ***")
        except:
            pass
