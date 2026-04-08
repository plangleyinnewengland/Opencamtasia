from pywinauto import Application, Desktop

# Find camtasia
for w in Desktop(backend="uia").windows():
    try:
        title = w.window_text()
        if "Camtasia" in title:
            pid = w.process_id()
            app = Application(backend="uia").connect(process=pid)
            editor = app.top_window()
            print(f"Window: '{editor.window_text()}'")
            # Look for menu bar
            for child in editor.children():
                ctype = child.element_info.control_type
                txt = child.window_text()
                cls = child.friendly_class_name()
                print(f"  {cls} | '{txt}' | type={ctype}")
                if ctype in ("MenuBar", "Menu", "ToolBar"):
                    for item in child.children():
                        print(f"    {item.friendly_class_name()} | '{item.window_text()}' | type={item.element_info.control_type}")
            break
    except Exception as e:
        print(f"Error: {e}")
