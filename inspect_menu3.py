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

# Try win32 backend which may see classic menus
try:
    app_win32 = Application(backend="win32").connect(process=pid)
    win = app_win32.top_window()
    print(f"win32 window: '{win.window_text()}'")
    try:
        menu = win.menu()
        print("Menu items:")
        for item in menu.items():
            print(f"  {item.text()}")
    except Exception as e:
        print(f"No win32 menu: {e}")
except Exception as e:
    print(f"win32 connect failed: {e}")

# Try accessing with the UIA approach and clicking the hamburger/file area
app = Application(backend="uia").connect(process=pid)
editor = app.top_window()

# Dump ALL top-level children names/types to find what could be the menu trigger
print("\nAll top-level children:")
for c in editor.children():
    try:
        r = c.rectangle()
        print(f"  {c.friendly_class_name()} | '{c.window_text()}' | type={c.element_info.control_type} | rect=({r.left},{r.top},{r.right},{r.bottom})")
    except:
        pass

# Try looking deeper in the Custom controls (these often contain ribbon/menu)
print("\nCustom control children:")
for c in editor.children():
    try:
        if c.element_info.control_type == "Custom":
            for c2 in c.children():
                r2 = c2.rectangle()
                print(f"  {c2.friendly_class_name()} | '{c2.window_text()}' | type={c2.element_info.control_type} | rect=({r2.left},{r2.top},{r2.right},{r2.bottom})")
                for c3 in c2.children():
                    r3 = c3.rectangle()
                    txt = c3.window_text()
                    if txt.strip():
                        print(f"    {c3.friendly_class_name()} | '{txt}' | type={c3.element_info.control_type} | rect=({r3.left},{r3.top},{r3.right},{r3.bottom})")
    except:
        pass
