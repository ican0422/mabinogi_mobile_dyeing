import tkinter as tk
from tkinter import colorchooser
import colorsys

class ColorPickerRow:
    def __init__(self, master, title, on_update_callback, must_include_index=None, index=0):
        self.master = master
        self.index = index
        self.must_include_index = must_include_index

        self.frame = tk.LabelFrame(master, text=title)
        self.frame.pack(pady=5, fill="x")

        self.hex_var = tk.StringVar()
        self.rgb_vars = [tk.StringVar(), tk.StringVar(), tk.StringVar()]

        # HEX 영역
        hex_frame = tk.Frame(self.frame)
        hex_frame.pack(anchor="w", padx=5)

        tk.Label(hex_frame, text="HEX").pack(side=tk.LEFT)
        self.hex_entry = tk.Entry(hex_frame, textvariable=self.hex_var, width=10)
        self.hex_entry.pack(side=tk.LEFT, padx=2)

        # 색상 미리보기
        self.preview_canvas = tk.Canvas(hex_frame, width=20, height=20, bd=1, relief='solid', bg="#FFFFFF")
        self.preview_canvas.pack(side=tk.LEFT, padx=4)

        # 색상 선택 버튼
        self.color_btn = tk.Button(hex_frame, text="색상 선택", command=self.open_color_picker)
        self.color_btn.pack(side=tk.LEFT, padx=2)

        # 반드시 포함 체크박스
        if self.must_include_index is not None:
            self.must_radio = tk.Radiobutton(
                hex_frame,
                text="반드시 포함",
                variable=self.must_include_index,
                value=self.index
            )
            self.must_radio.pack(side=tk.LEFT, padx=5)

        # RGB 영역
        rgb_frame = tk.Frame(self.frame)
        rgb_frame.pack(anchor="w", padx=5)
        for i, ch in enumerate("RGB"):
            tk.Label(rgb_frame, text=f"{ch}:").pack(side=tk.LEFT)
            entry = tk.Entry(rgb_frame, textvariable=self.rgb_vars[i], width=4)
            entry.pack(side=tk.LEFT, padx=2)

        # HSV 출력
        self.hsv_label = tk.Label(self.frame, text="명도: - / 채도: - / 색상: -")
        self.hsv_label.pack(anchor="w", padx=5, pady=(2, 0))

        # 바인딩
        self.hex_var.trace_add("write", lambda *args: self.update_rgb_from_hex())
        for var in self.rgb_vars:
            var.trace_add("write", lambda *args: self.update_hex_from_rgb())

        self.on_update_callback = on_update_callback

    def open_color_picker(self):
        rgb_tuple, hex_code = colorchooser.askcolor()
        if hex_code:
            self.hex_var.set(hex_code.upper())
            self.update_rgb_from_hex()

    def update_rgb_from_hex(self):
        hex_code = self.hex_var.get()
        if hex_code.startswith("#") and len(hex_code) == 7:
            try:
                r = int(hex_code[1:3], 16)
                g = int(hex_code[3:5], 16)
                b = int(hex_code[5:7], 16)
                for i, val in enumerate((r, g, b)):
                    self.rgb_vars[i].set(str(val))
                self.update_hsv_display(r, g, b)
                self.update_preview_color(hex_code)
                self.on_update_callback()
            except:
                pass

    def update_hex_from_rgb(self):
        try:
            r, g, b = [int(v.get()) for v in self.rgb_vars]
            hex_code = f"#{r:02X}{g:02X}{b:02X}"
            self.hex_var.set(hex_code)
            self.update_hsv_display(r, g, b)
            self.update_preview_color(hex_code)
            self.on_update_callback()
        except:
            pass

    def update_hsv_display(self, r, g, b):
        h, s, v = colorsys.rgb_to_hsv(r/255.0, g/255.0, b/255.0)
        h = round(h * 360, 1)
        s = round(s * 255, 1)
        v = round(v * 255, 1)
        self.hsv_label.config(text=f"명도: {v} / 채도: {s} / 색상: {h}")

    def update_preview_color(self, hex_color):
        self.preview_canvas.config(bg=hex_color)

    def get_rgb(self):
        try:
            return tuple(int(v.get()) for v in self.rgb_vars)
        except:
            return None

    def get_hex(self):
        return self.hex_var.get()
