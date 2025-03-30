# import tkinter as tk
# from tkinter import colorchooser
# from tone_utils import detect_tone_regions
# import cv2
# import numpy as np
# import mss
# from PIL import Image

# class ToneColorSelector:
#     def __init__(self, master):
#         self.master = master
#         self.master.title("톤 기반 색상 선택")

#         self.tone_labels = [tk.Label(master, text=f"영역 {i+1} 톤: 분석 전") for i in range(3)]
#         for lbl in self.tone_labels:
#             lbl.pack(pady=2)

#         self.select_btn = tk.Button(master, text="선택한 구역에서 톤 자동 감지", command=self.auto_detect_tone)
#         self.select_btn.pack(pady=10)

#         self.color_vars = [tk.StringVar() for _ in range(3)]
#         self.rgb_vars = [[tk.StringVar(), tk.StringVar(), tk.StringVar()] for _ in range(3)]
#         self.color_canvases = []

#         for i, label in enumerate(["좌 영역 색상", "중앙 영역 색상", "우 영역 색상"]):
#             frame = tk.Frame(master)
#             frame.pack(pady=2)

#             canvas = tk.Canvas(frame, width=20, height=20, bg="white", highlightthickness=1, relief='solid')
#             canvas.pack(side=tk.LEFT, padx=2)
#             self.color_canvases.append(canvas)

#             btn = tk.Button(frame, text=label, command=lambda idx=i: self.choose_color(idx))
#             btn.pack(side=tk.LEFT, padx=3)

#             entry = tk.Entry(frame, textvariable=self.color_vars[i], width=10)
#             entry.pack(side=tk.LEFT)
#             self.color_vars[i].trace_add("write", lambda *args, idx=i: self.update_color_preview(idx))

#             rgb_frame = tk.Frame(master)
#             rgb_frame.pack(pady=1)
#             for j, ch in enumerate("RGB"):
#                 tk.Label(rgb_frame, text=f"{ch}").pack(side=tk.LEFT)
#                 entry = tk.Entry(rgb_frame, textvariable=self.rgb_vars[i][j], width=4)
#                 entry.pack(side=tk.LEFT)
#             # RGB -> HEX + 색상 반영 trace 추가
#             for j in range(3):
#                 self.rgb_vars[i][j].trace_add("write", lambda *args, idx=i: self.update_from_rgb(idx))

#         self.confirm_btn = tk.Button(master, text="확인", command=self.print_result)
#         self.confirm_btn.pack(pady=10)

#         self.selected_region = None

#     def set_region(self, region):
#         self.selected_region = region

#     def auto_detect_tone(self):
#         if self.selected_region is None:
#             tk.messagebox.showerror("오류", "먼저 영역을 지정하세요")
#             return

#         with mss.mss() as sct:
#             img = sct.grab(self.selected_region)
#             img_pil = Image.frombytes('RGB', img.size, img.rgb)
#             img_np = np.array(img_pil)
#             tones = detect_tone_regions(img_np)  # 리스트: [{hue, saturation, value, tone}]

#         for i, tone_info in enumerate(tones):
#             tone_name = tone_info['tone']
#             h, s, v = tone_info['hue'], tone_info['saturation'], tone_info['value']
#             self.tone_labels[i].config(
#                 text=f"영역 {i+1} 톤: 명도={v:.1f}, 채도={s:.1f}, 색상={h:.1f} → {tone_name}"
#             )

#             hsv_norm = np.uint8([[[int(h/2), int(s), int(v)]]])  # HSV는 H:0~179
#             bgr = cv2.cvtColor(hsv_norm, cv2.COLOR_HSV2BGR)[0][0]
#             r, g, b = int(bgr[2]), int(bgr[1]), int(bgr[0])
#             hex_code = f"#{r:02x}{g:02x}{b:02x}"

#             self.color_vars[i].set(hex_code)
#             self.rgb_vars[i][0].set(str(r))
#             self.rgb_vars[i][1].set(str(g))
#             self.rgb_vars[i][2].set(str(b))
#             self.update_color_canvas(i, r, g, b)


#     def choose_color(self, idx):
#         color = colorchooser.askcolor()[0]
#         if color:
#             r, g, b = map(int, color)
#             hex_code = f"#{r:02x}{g:02x}{b:02x}"
#             self.color_vars[idx].set(hex_code)
#             self.rgb_vars[idx][0].set(str(r))
#             self.rgb_vars[idx][1].set(str(g))
#             self.rgb_vars[idx][2].set(str(b))
#             self.update_color_canvas(idx, r, g, b)

#     def update_color_canvas(self, idx, r, g, b):
#         color = f"#{r:02x}{g:02x}{b:02x}"
#         self.color_canvases[idx].config(bg=color)

#     def update_color_preview(self, idx):
#         hex_code = self.color_vars[idx].get()
#         if not hex_code.startswith('#') or len(hex_code) != 7:
#             return
#         try:
#             r = int(hex_code[1:3], 16)
#             g = int(hex_code[3:5], 16)
#             b = int(hex_code[5:7], 16)
#         except ValueError:
#             return

#         self.rgb_vars[idx][0].set(str(r))
#         self.rgb_vars[idx][1].set(str(g))
#         self.rgb_vars[idx][2].set(str(b))
#         self.update_color_canvas(idx, r, g, b)

#     def update_from_rgb(self, idx):
#         try:
#             r = int(self.rgb_vars[idx][0].get())
#             g = int(self.rgb_vars[idx][1].get())
#             b = int(self.rgb_vars[idx][2].get())
#             if not (0 <= r <= 255 and 0 <= g <= 255 and 0 <= b <= 255):
#                 return
#         except ValueError:
#             return
#         hex_code = f"#{r:02x}{g:02x}{b:02x}"
#         self.color_vars[idx].set(hex_code)
#         self.update_color_canvas(idx, r, g, b)

#     def print_result(self):
#         result = {
#             'left': self.color_vars[0].get(),
#             'center': self.color_vars[1].get(),
#             'right': self.color_vars[2].get(),
#         }
#         print("[선택된 색상 값]", result)
#         tk.messagebox.showinfo("선택 완료", f"선택된 색상:\n좌: {result['left']}\n중앙: {result['center']}\n우: {result['right']}")

# if __name__ == "__main__":
#     root = tk.Tk()
#     selector = ToneColorSelector(root)
#     selector.set_region({
#         'left': 500,
#         'top': 300,
#         'width': 300,
#         'height': 300
#     })
#     root.mainloop()
