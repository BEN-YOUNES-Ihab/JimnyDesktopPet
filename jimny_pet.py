"""
JimnyDesktopPet for Windows
A pixel-art Suzuki Jimny that drives across your desktop.
"""

import tkinter as tk
import os, sys, math, random

def res(rel):
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    p = os.path.join(base, rel)
    if os.path.exists(p): return p
    p2 = os.path.join(os.getcwd(), rel)
    return p2 if os.path.exists(p2) else p

class Cfg:
    scale    = 3.0
    speed    = 3.0
    paused   = False
    tick_ms  = 16
    frame_ms = 110
    roam     = False  # True = random horizontal + vertical movement

cfg = Cfg()

class Animator:
    def __init__(self):
        self.seqs  = {}
        self.seq   = "drive"
        self.idx   = 0
        self.right = True
        self._load()

    def _load(self):
        root = res("frames")
        if not os.path.isdir(root): return
        for name in os.listdir(root):
            d = os.path.join(root, name)
            if os.path.isdir(d):
                files = sorted(f for f in os.listdir(d) if f.endswith(".png"))
                if files:
                    self.seqs[name] = [os.path.join(d, f) for f in files]

    def frame_path(self):
        s = self.seqs.get(self.seq)
        return s[self.idx % len(s)] if s else None

    def advance(self):
        s = self.seqs.get(self.seq)
        if s: self.idx = (self.idx + 1) % len(s)

    def switch(self, name):
        if name in self.seqs and name != self.seq:
            self.seq = name
            self.idx = 0

    def seq_len(self):
        return len(self.seqs.get(self.seq, []))


class Jimny:
    SPRITE_W = 80
    SPRITE_H = 56

    def __init__(self, root):
        self.root   = root
        self.anim   = Animator()
        self._cache = {}
        self._ref   = None
        self._drag  = False
        self._doff  = (0, 0)
        self._wcool = 0
        self._last_scale = cfg.scale
        self._vy = 0.0          # vertical velocity for roam mode
        self._roam_cool = 0     # ticks until next direction nudge

        self.sw = root.winfo_screenwidth()
        self.sh = root.winfo_screenheight()

        w, h = self._size()
        self.x = float(self.sw // 4)
        self.y = float(self.sh - h - 50)

        root.overrideredirect(True)
        root.attributes("-topmost", True)
        root.attributes("-transparentcolor", "#010101")
        root.configure(bg="#010101")

        self.canvas = tk.Canvas(
            root, width=w, height=h,
            bg="#010101", highlightthickness=0, borderwidth=0
        )
        self.canvas.pack()
        self._img_id = self.canvas.create_image(0, 0, anchor="nw")

        self.canvas.bind("<ButtonPress-1>",   self._press)
        self.canvas.bind("<B1-Motion>",       self._motion)
        self.canvas.bind("<ButtonRelease-1>", self._release)
        self.canvas.bind("<Button-3>",        self._rclick)
        self.canvas.configure(cursor="hand2")

        self._apply_geom()
        self._draw_frame()
        root.after(cfg.tick_ms,  self._move)
        root.after(cfg.frame_ms, self._tick)
        root.after(500,          self._stay_on_top)

    def _size(self):
        return int(self.SPRITE_W * cfg.scale), int(self.SPRITE_H * cfg.scale)

    def _apply_geom(self):
        w, h = self._size()
        self.root.geometry(f"{w}x{h}+{int(self.x)}+{int(self.y)}")

    def _stay_on_top(self):
        self.root.attributes("-topmost", True)
        self.root.after(500, self._stay_on_top)

    def _get_image(self, path):
        key = f"{path}|{cfg.scale:.2f}|{self.anim.right}"
        if key not in self._cache:
            try:
                from PIL import Image, ImageOps, ImageTk
                img = Image.open(path).convert("RGBA")
                w, h = self._size()
                img = img.resize((w, h), Image.NEAREST)
                if not self.anim.right:
                    img = ImageOps.mirror(img)
                r, g, b, a = img.split()
                bg = Image.new("RGB", img.size, (1, 1, 1))
                bg.paste(img.convert("RGB"), mask=a)
                self._cache[key] = ImageTk.PhotoImage(bg)
            except Exception as e:
                print(f"Image error: {e}")
                return None
        return self._cache[key]

    def _draw_frame(self):
        if cfg.scale != self._last_scale:
            w, h = self._size()
            self.canvas.config(width=w, height=h)
            self._last_scale = cfg.scale
            self._cache.clear()

        p = self.anim.frame_path()
        if p:
            im = self._get_image(p)
            if im:
                self.canvas.itemconfig(self._img_id, image=im)
                self._ref = im

    def _move(self):
        if not cfg.paused and not self._drag:
            spd = cfg.speed * max(cfg.scale, 1.0) * 0.4
            self.x += spd if self.anim.right else -spd

            w, h = self._size()

            # ── Roam mode: random vertical movement ──
            if cfg.roam:
                if self._roam_cool <= 0:
                    self._vy = random.uniform(-spd, spd)
                    self._roam_cool = random.randint(40, 120)
                else:
                    self._roam_cool -= 1
                self.y += self._vy
                if self.y < 0:
                    self.y = 0.0
                    self._vy = abs(self._vy)
                elif self.y + h > self.sh:
                    self.y = float(self.sh - h)
                    self._vy = -abs(self._vy)
            else:
                self._vy = 0.0

            # Bounce off left/right edges
            if self.x + w >= self.sw:
                self.x = float(self.sw - w)
                self.anim.right = False
                self._cache.clear()
            elif self.x <= 0:
                self.x = 0.0
                self.anim.right = True
                self._cache.clear()

            if self._wcool > 0:
                self._wcool -= 1
            elif random.random() < 0.0008 and "water_crossing" in self.anim.seqs:
                self.anim.switch("water_crossing")

            if self.anim.seq == "water_crossing" and self.anim.idx >= self.anim.seq_len() - 1:
                self.anim.switch("drive")
                self._wcool = random.randint(900, 1500)

            self._apply_geom()
        self.root.after(cfg.tick_ms, self._move)

    def _tick(self):
        if not cfg.paused:
            self.anim.advance()
            self._draw_frame()
        self.root.after(cfg.frame_ms, self._tick)

    def _press(self, e):
        self._drag = True
        self._doff = (e.x_root - self.x, e.y_root - self.y)
        self.canvas.configure(cursor="fleur")

    def _dbl(self, e):
        pass  # double-click no longer needed

    def _motion(self, e):
        if self._drag:
            ox, oy = self._doff
            self.x = e.x_root - ox
            self.y = e.y_root - oy
            self._apply_geom()

    def _release(self, e):
        if self._drag:
            self._drag = False
            self.canvas.configure(cursor="hand2")

    def _rclick(self, e):
        m = tk.Menu(self.root, tearoff=0)
        m.add_command(label="⚙  Settings…", command=self._settings)
        m.add_command(label="▶  Resume" if cfg.paused else "⏸  Pause", command=self._pause)
        m.add_separator()
        m.add_command(label="✕  Quit Jimny", command=self.root.destroy)
        m.tk_popup(e.x_root, e.y_root)

    def _pause(self):
        cfg.paused = not cfg.paused

    def _settings(self):
        if hasattr(self, "_sw") and self._sw.winfo_exists():
            self._sw.lift(); return

        w = tk.Toplevel(self.root)
        w.title("Jimny Settings")
        w.attributes("-topmost", True)
        w.resizable(False, False)
        self._sw = w

        try:
            import ctypes
            hwnd = ctypes.windll.user32.GetParent(w.winfo_id())
            if not hwnd: hwnd = w.winfo_id()
            GWL_EXSTYLE = -20; WS_EX_LAYERED = 0x80000
            style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
            ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style & ~WS_EX_LAYERED)
        except Exception:
            pass

        tk.Label(w, text="Jimny Desktop Pet", font=("Segoe UI", 13, "bold")).pack(padx=20, pady=(16, 4))

        # ── Size (0.5 to 8.0 by 0.5) ──
        tk.Label(w, text="Size", anchor="w").pack(fill="x", padx=20)
        sv = tk.DoubleVar(value=cfg.scale)
        def on_size(v): cfg.scale = float(v)
        tk.Scale(w, from_=0.5, to=8.0, resolution=0.5, orient="horizontal",
                 variable=sv, command=on_size, length=240).pack(padx=20, pady=4)

        # ── Speed ──
        tk.Label(w, text="Speed", anchor="w").pack(fill="x", padx=20)
        spv = tk.DoubleVar(value=cfg.speed)
        def on_spd(v): cfg.speed = float(v)
        tk.Scale(w, from_=0.5, to=10.0, resolution=0.5, orient="horizontal",
                 variable=spv, command=on_spd, length=240).pack(padx=20, pady=4)

        # ── Roam mode ──
        rv = tk.BooleanVar(value=cfg.roam)
        def on_roam():
            cfg.roam = rv.get()
            if not cfg.roam:
                self._vy = 0.0
        tk.Checkbutton(w, text="Roam freely (random horizontal + vertical)", variable=rv, command=on_roam
                       ).pack(padx=20, pady=6, anchor="w")

        # ── Pause ──
        pv = tk.BooleanVar(value=cfg.paused)
        def on_pause(): cfg.paused = pv.get()
        tk.Checkbutton(w, text="Paused", variable=pv, command=on_pause
                       ).pack(padx=20, pady=6, anchor="w")

        tk.Button(w, text="Quit Jimny", command=self.root.destroy,
                  fg="white", bg="#cc4444", font=("Segoe UI", 10, "bold"),
                  relief="flat", padx=12, pady=5).pack(pady=(4, 16))


def main():
    root = tk.Tk()
    root.withdraw()
    root.title("JimnyPet")
    Jimny(root)
    root.deiconify()
    root.mainloop()

if __name__ == "__main__":
    main()