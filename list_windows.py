from pywinauto import Desktop

desktop = Desktop(backend="uia")
windows = desktop.windows()
print("=== All top-level windows ===")
for w in windows:
    try:
        title = w.window_text()
        if title.strip():
            print(f"  '{title}'")
    except:
        pass
