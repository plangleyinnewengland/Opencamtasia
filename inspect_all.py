from pywinauto import Application, Desktop

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

# Dump ALL descendants - every single one
print("=== ALL descendants ===")
for d in editor.descendants():
    try:
        txt = d.window_text()
        ctype = d.element_info.control_type
        cls = d.friendly_class_name()
        r = d.rectangle()
        if txt.strip() or ctype in ("Button", "MenuItem", "Menu", "MenuBar"):
            print(f"{cls} | '{txt}' | type={ctype} | ({r.left},{r.top},{r.right},{r.bottom})")
    except:
        pass
