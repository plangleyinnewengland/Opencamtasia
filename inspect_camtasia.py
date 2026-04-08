from pywinauto import Desktop

desktop = Desktop(backend="uia")
windows = desktop.windows()
for w in windows:
    try:
        title = w.window_text()
        if "Camtasia" in title or "TechSmith" in title:
            print(f"Window: {title}")
            print("--- Children (first 2 levels) ---")
            def dump(ctrl, depth=0):
                if depth > 2:
                    return
                try:
                    indent = "  " * depth
                    ctype = ctrl.element_info.control_type
                    txt = ctrl.window_text()
                    cls = ctrl.friendly_class_name()
                    print(f"{indent}{cls} | '{txt}' | type={ctype}")
                except:
                    pass
                if depth < 2:
                    for c in ctrl.children():
                        dump(c, depth + 1)
            dump(w)
    except Exception as e:
        pass
