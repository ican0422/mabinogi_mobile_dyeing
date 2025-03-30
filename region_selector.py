# region_selector.py

import tkinter as tk

class RegionSelector:
    def __init__(self, on_complete=None):  # ✅ 추가
        self.start_x = self.start_y = 0
        self.rect = None
        self.region = None
        self.on_complete = on_complete  # ✅ 추가

    def select(self):
        self.root = tk.Tk()
        self.root.attributes("-fullscreen", True)
        self.root.attributes("-alpha", 0.3)
        self.root.configure(bg="black")
        self.root.bind("<Escape>", lambda e: self.exit(None))  # ✅ 콜백 종료

        self.canvas = tk.Canvas(self.root, cursor="cross", bg="gray", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)

        self.root.mainloop()

    def exit(self, region):
        self.region = region
        self.root.destroy()
        if self.on_complete:
            self.on_complete(region)

    def on_press(self, event):
        self.start_x, self.start_y = event.x, event.y
        self.rect = self.canvas.create_rectangle(
            self.start_x, self.start_y, self.start_x, self.start_y,
            outline="red", width=2)

    def on_drag(self, event):
        self.canvas.coords(self.rect, self.start_x, self.start_y, event.x, event.y)

    def on_release(self, event):
        end_x, end_y = event.x, event.y
        x1, y1 = min(self.start_x, end_x), min(self.start_y, end_y)
        x2, y2 = max(self.start_x, end_x), max(self.start_y, end_y)
        width = max(1, x2 - x1)
        height = max(1, y2 - y1)
        self.exit((x1, y1, width, height))
