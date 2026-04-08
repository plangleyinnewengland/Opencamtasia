"""
Camtasia Importer
Lets you select media files and imports them sequentially onto the timeline
of a new Camtasia project, then opens it in Camtasia.
"""

import os
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pathlib import Path
import camtasia

CAMTASIA_EXE = r"C:\Program Files\TechSmith\Camtasia 2025\CamtasiaStudio.exe"
DEFAULT_PROJECTS_DIR = str(Path.home() / "Documents")
IMAGE_DURATION_FRAMES = 150  # 5 seconds at 30fps for still images


class CamtasiaImporterApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Camtasia Importer")
        self.resizable(False, False)
        self.configure(padx=16, pady=12, bg="#f0f0f0")
        self._files = []
        self._build_ui()

    # ── UI ────────────────────────────────────────────────────────────────────

    def _build_ui(self):
        style = ttk.Style(self)
        style.theme_use("clam")

        # ── File list ──
        list_frame = tk.LabelFrame(self, text="Selected Media Files", bg="#f0f0f0", padx=6, pady=6)
        list_frame.grid(row=0, column=0, columnspan=3, sticky="ew", pady=(0, 8))

        self._listbox = tk.Listbox(list_frame, width=60, height=10, selectmode=tk.SINGLE,
                                   activestyle="dotbox", font=("Segoe UI", 9))
        self._listbox.pack(side="left", fill="both", expand=True)

        sb = ttk.Scrollbar(list_frame, orient="vertical", command=self._listbox.yview)
        sb.pack(side="right", fill="y")
        self._listbox.configure(yscrollcommand=sb.set)

        # ── Buttons row ──
        btn_frame = tk.Frame(self, bg="#f0f0f0")
        btn_frame.grid(row=1, column=0, columnspan=3, sticky="ew", pady=(0, 10))

        ttk.Button(btn_frame, text="➕  Add Files",   command=self._add_files).pack(side="left", padx=(0, 4))
        ttk.Button(btn_frame, text="🗑  Remove",       command=self._remove_selected).pack(side="left", padx=4)
        ttk.Button(btn_frame, text="⬆  Move Up",      command=self._move_up).pack(side="left", padx=4)
        ttk.Button(btn_frame, text="⬇  Move Down",    command=self._move_down).pack(side="left", padx=4)
        ttk.Button(btn_frame, text="✖  Clear All",    command=self._clear_all).pack(side="left", padx=4)

        # ── Project name ──
        tk.Label(self, text="Project Name:", bg="#f0f0f0", font=("Segoe UI", 9)).grid(
            row=2, column=0, sticky="w", pady=2)
        self._project_name = tk.StringVar(value="My Project")
        ttk.Entry(self, textvariable=self._project_name, width=40).grid(
            row=2, column=1, sticky="ew", padx=6)

        # ── Save location ──
        tk.Label(self, text="Save Location:", bg="#f0f0f0", font=("Segoe UI", 9)).grid(
            row=3, column=0, sticky="w", pady=2)
        self._save_dir = tk.StringVar(value=DEFAULT_PROJECTS_DIR)
        ttk.Entry(self, textvariable=self._save_dir, width=40).grid(
            row=3, column=1, sticky="ew", padx=6)
        ttk.Button(self, text="Browse…", command=self._browse_save_dir).grid(
            row=3, column=2, padx=(0, 0))

        # ── Image duration ──
        tk.Label(self, text="Image Duration (sec):", bg="#f0f0f0", font=("Segoe UI", 9)).grid(
            row=4, column=0, sticky="w", pady=(6, 2))
        self._image_dur = tk.IntVar(value=5)
        ttk.Spinbox(self, from_=1, to=60, textvariable=self._image_dur, width=6).grid(
            row=4, column=1, sticky="w", padx=6)

        # ── Open after creating ──
        self._open_after = tk.BooleanVar(value=True)
        ttk.Checkbutton(self, text="Open project in Camtasia after creating",
                        variable=self._open_after).grid(
            row=5, column=0, columnspan=3, sticky="w", pady=(6, 0))

        # ── Status ──
        self._status = tk.StringVar(value="Add files to get started.")
        tk.Label(self, textvariable=self._status, bg="#f0f0f0",
                 font=("Segoe UI", 8), fg="#555").grid(
            row=6, column=0, columnspan=3, sticky="w", pady=(6, 0))

        # ── Create button ──
        ttk.Button(self, text="▶  Create Project", command=self._create_project,
                   style="Accent.TButton").grid(
            row=7, column=0, columnspan=3, pady=(10, 0), ipadx=10, ipady=4)

        self.columnconfigure(1, weight=1)

    # ── Event handlers ────────────────────────────────────────────────────────

    def _add_files(self):
        files = filedialog.askopenfilenames(
            title="Select Media Files",
            filetypes=[
                ("All Supported", "*.mp4 *.mov *.avi *.wmv *.mkv *.mp3 *.wav *.m4a *.png *.jpg *.jpeg *.gif *.bmp"),
                ("Video",  "*.mp4 *.mov *.avi *.wmv *.mkv"),
                ("Audio",  "*.mp3 *.wav *.m4a"),
                ("Images", "*.png *.jpg *.jpeg *.gif *.bmp"),
                ("All Files", "*.*"),
            ]
        )
        for f in files:
            if f not in self._files:
                self._files.append(f)
                self._listbox.insert(tk.END, os.path.basename(f))
        self._update_status()

    def _remove_selected(self):
        sel = self._listbox.curselection()
        if sel:
            idx = sel[0]
            self._listbox.delete(idx)
            del self._files[idx]
        self._update_status()

    def _move_up(self):
        sel = self._listbox.curselection()
        if sel and sel[0] > 0:
            idx = sel[0]
            self._files[idx - 1], self._files[idx] = self._files[idx], self._files[idx - 1]
            self._refresh_listbox(idx - 1)

    def _move_down(self):
        sel = self._listbox.curselection()
        if sel and sel[0] < len(self._files) - 1:
            idx = sel[0]
            self._files[idx], self._files[idx + 1] = self._files[idx + 1], self._files[idx]
            self._refresh_listbox(idx + 1)

    def _clear_all(self):
        self._files.clear()
        self._listbox.delete(0, tk.END)
        self._update_status()

    def _browse_save_dir(self):
        d = filedialog.askdirectory(title="Choose Save Location")
        if d:
            self._save_dir.set(d)

    def _refresh_listbox(self, select_idx=None):
        self._listbox.delete(0, tk.END)
        for f in self._files:
            self._listbox.insert(tk.END, os.path.basename(f))
        if select_idx is not None:
            self._listbox.selection_set(select_idx)
            self._listbox.activate(select_idx)

    def _update_status(self):
        n = len(self._files)
        self._status.set(f"{n} file{'s' if n != 1 else ''} selected." if n else "Add files to get started.")

    # ── Project creation ──────────────────────────────────────────────────────

    def _create_project(self):
        if not self._files:
            messagebox.showwarning("No Files", "Please add at least one media file.")
            return

        name = self._project_name.get().strip()
        if not name:
            messagebox.showwarning("No Name", "Please enter a project name.")
            return

        save_dir = self._save_dir.get().strip()
        proj_path = os.path.join(save_dir, f"{name}.cmproj")

        if os.path.exists(proj_path):
            if not messagebox.askyesno("Overwrite?", f"'{proj_path}' already exists. Overwrite?"):
                return
            import shutil
            shutil.rmtree(proj_path)

        self._status.set("Creating project…")
        self.update_idletasks()

        try:
            camtasia.new_project(proj_path)
            proj = camtasia.load_project(proj_path)
            edit_rate = proj.edit_rate  # frames per second
            image_dur_frames = self._image_dur.get() * edit_rate

            track = list(proj.timeline.tracks)[0]
            cursor = 0  # current frame position on the timeline

            for file_path in self._files:
                self._status.set(f"Importing {os.path.basename(file_path)}…")
                self.update_idletasks()

                bin_media = proj.media_bin.import_media(file_path)
                ext = Path(file_path).suffix.lower()
                is_image = ext in {".png", ".jpg", ".jpeg", ".gif", ".bmp"}
                duration = image_dur_frames if is_image else bin_media.range[1].to_frame()

                track.medias.add_media(bin_media, start=cursor, duration=duration)
                cursor += duration

            proj.save()
            self._status.set(f"✅ Project saved: {proj_path}")

            if self._open_after.get():
                subprocess.Popen([CAMTASIA_EXE, proj_path])

        except Exception as e:
            messagebox.showerror("Error", str(e))
            self._status.set("❌ Error occurred.")


if __name__ == "__main__":
    app = CamtasiaImporterApp()
    app.mainloop()
