from pywinauto import Application, Desktop
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
print(f"Window: '{editor.window_text()}'")

# Dump EVERYTHING recursively with positions, up to depth 6
# Focus on items in the title bar area (y < 280 based on main content starting at 280)
def dump_all(ctrl, depth=0):
    if depth > 5:
        return
    try:
        txt = ctrl.window_text()
        ctype = ctrl.element_info.control_type
        cls = ctrl.friendly_class_name()
        r = ctrl.rectangle()
        indent = "  " * depth
        # Show everything regardless
        line = f"{indent}{cls} | '{txt}' | type={ctype} | ({r.left},{r.top},{r.right},{r.bottom})"
        print(line)
    except:
        return
    try:
        for c in ctrl.children():
            dump_all(c, depth + 1)
    except:
        pass

# Only dump the title bar / toolbar area
print("=== Title bar / top area elements ===")
for c in editor.children():
    try:
        r = c.rectangle()
        # Title bar area (above the main content at y=280)
        if r.bottom <= 285 or r.top <= 250:
            dump_all(c, 1)
    except:
        pass

# Also look at the left panel area which might have import buttons
print("\n=== Left panel area ===")
for c in editor.descendants():
    try:
        txt = c.window_text()
        if txt and any(k in txt.lower() for k in ["import", "file", "media", "bin", "plus", "add"]):
            r = c.rectangle()
            print(f"  {c.friendly_class_name()} | '{txt}' | type={c.element_info.control_type} | ({r.left},{r.top},{r.right},{r.bottom})")
    except:
        pass
