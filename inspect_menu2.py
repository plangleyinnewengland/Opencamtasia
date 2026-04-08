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

# Dump ALL descendants up to depth 3, filtering for anything menu/file/import related
def dump_all(ctrl, depth=0, max_depth=4):
    if depth > max_depth:
        return
    try:
        txt = ctrl.window_text()
        ctype = ctrl.element_info.control_type
        cls = ctrl.friendly_class_name()
        indent = "  " * depth
        keywords = ["file", "import", "media", "menu", "record", "edit", "view", "help"]
        if any(k in txt.lower() for k in keywords) or ctype in ("MenuBar", "Menu", "MenuItem") or depth < 2:
            print(f"{indent}{cls} | '{txt}' | type={ctype}")
    except:
        pass
    try:
        for c in ctrl.children():
            dump_all(c, depth + 1, max_depth)
    except:
        pass

dump_all(editor)
