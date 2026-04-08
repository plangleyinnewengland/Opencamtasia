from pywinauto import Application, Desktop
from pywinauto.keyboard import send_keys
import time

# Find camtasia
for w in Desktop(backend="uia").windows():
    try:
        title = w.window_text()
        if "Camtasia" in title:
            pid = w.process_id()
            break
    except:
        pass

app = Application(backend="uia").connect(process=pid)
editor = app.top_window()
editor.set_focus()
time.sleep(1)

# Try all the buttons without text - list click locations
r = editor.rectangle()
print(f"Window: ({r.left},{r.top},{r.right},{r.bottom})")

# List ALL buttons
print("\n=== ALL Buttons ===")
buttons = []
for d in editor.descendants():
    try:
        ctype = d.element_info.control_type
        if ctype == "Button":
            txt = d.window_text()
            r2 = d.rectangle()
            auto_id = d.element_info.automation_id
            print(f"  Button | '{txt}' | auto_id='{auto_id}' | ({r2.left},{r2.top},{r2.right},{r2.bottom})")
            buttons.append(d)
    except:
        pass

# Also try: press F10 or Alt to activate classic menus
print("\n=== Trying F10 to activate menus ===")
send_keys("{F10}")
time.sleep(2)

# Check for menus
for w2 in Desktop(backend="uia").windows():
    try:
        t = w2.window_text()
        ctype = w2.element_info.control_type
        if ctype in ("Menu", "Popup") or "menu" in t.lower():
            print(f"  '{t}' | type={ctype}")
    except:
        pass

# Check descendants for new menu items
for d in editor.descendants():
    try:
        txt = d.window_text()
        ctype = d.element_info.control_type
        if ctype == "MenuItem" and txt != "80%":
            r2 = d.rectangle()
            print(f"  MenuItem | '{txt}' | ({r2.left},{r2.top},{r2.right},{r2.bottom})")
    except:
        pass

# Escape
send_keys("{ESC}")
