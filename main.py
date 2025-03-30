import tkinter as tk
from tkinter import messagebox
import threading
import time
import mss
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageTk
from color_util import hex_to_rgb, total_color_distance
from controller import random_adjust
from detector import extract_dominant_colors, contains_all_target_colors
from region_selector import RegionSelector
from color_picker_ui import ColorPickerRow

VERSION = "v3.1.0"

class DyeToolGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("염색 자동화 도우미")

        version_label = tk.Label(root, text=VERSION, fg='gray')
        version_label.pack(pady=(5, 0))

        self.must_include_index = tk.IntVar(value=-1)  # -1은 선택 안 함

        self.color_pickers = []
        for i, title in enumerate(["좌 영역 색상", "중앙 영역 색상", "우 영역 색상"]):
            picker = ColorPickerRow(root, title, self.on_color_update, must_include_index=self.must_include_index, index=i)
            self.color_pickers.append(picker)

        self.tolerance = tk.IntVar(value=50)
        tk.Label(root, text="허용 오차 (정확도 기준)").pack()
        scale_frame = tk.Frame(root)
        scale_frame.pack(pady=5)
        tk.Scale(scale_frame, from_=0, to=100, orient='horizontal', variable=self.tolerance).pack(side=tk.LEFT)
        self.tolerance_entry = tk.Entry(scale_frame, textvariable=self.tolerance, width=5)
        self.tolerance_entry.pack(side=tk.LEFT, padx=5)

        tk.Button(root, text="팔레트 영역 지정하기", command=self.select_region).pack(pady=5)
        tk.Button(root, text="자동 인식 시작 (Ctrl+Enter)", command=self.start_detection).pack(pady=5)
        tk.Button(root, text="정지 (Esc)", command=self.stop_detection).pack(pady=5)

        self.log = tk.Text(root, height=10, width=50)
        self.log.pack(pady=10)

        self.preview_label = tk.Label(root)
        self.preview_label.pack(pady=5)

        self.region = None
        self.running = False

        self.root.bind('<Control-Return>', lambda e: self.start_detection())
        self.root.bind('<Escape>', lambda e: self.stop_detection())

    def on_color_update(self):
        pass

    def log_message(self, msg):
        self.log.insert(tk.END, f"{msg}\n")
        self.log.see(tk.END)

    def select_region(self):
        self.log_message("마우스로 화면을 드래그하여 영역을 지정하세요 (ESC로 취소)")

        def on_region_selected(region):
            if region:
                self.region = region
                self.log_message(f"✅ 영역이 지정되었습니다: {self.region}")
            else:
                self.log_message("❌ 영역 선택이 취소되었습니다.")

        selector = RegionSelector(on_complete=on_region_selected)
        threading.Thread(target=selector.select).start()

    def start_detection(self):
        if not self.region:
            messagebox.showerror("오류", "먼저 영역을 지정하세요.")
            return
        self.running = True
        thread = threading.Thread(target=self.run_detection)
        thread.start()

    def stop_detection(self):
        self.running = False
        self.log_message("⛔ 자동화를 수동으로 중지했습니다.")

    def run_detection(self):
        self.log_message("흰 원 탐지 시작...")

        with mss.mss() as sct:
            monitor = {
                "left": self.region[0],
                "top": self.region[1],
                "width": self.region[2],
                "height": self.region[3]
            }
            target_colors = [hex_to_rgb(picker.get_hex()) for picker in self.color_pickers]
            must_index = self.must_include_index.get()
            must_color = target_colors[must_index] if must_index != -1 else None
            center = (self.region[0] + self.region[2] // 2, self.region[1] + self.region[3] // 2)

            # 팔레트에서 색상을 찾을 때까지 반복 탐색
            attempts = 0
            max_attempts = 30
            while self.running and attempts < max_attempts:
                attempts += 1
                sct_img = sct.grab(monitor)
                img = Image.frombytes('RGB', sct_img.size, sct_img.rgb)
                img_np = np.array(img)

                dominants = extract_dominant_colors(img_np)
                if contains_all_target_colors(dominants, target_colors, threshold=self.tolerance.get()):
                    self.log_message("🎯 팔레트 내에 모든 목표 색상이 존재합니다.")
                    break
                else:
                    self.log_message(f"⏳ ({attempts}/{max_attempts}) 팔레트에 색상이 감지되지 않아 조작을 시도합니다...")
                    random_adjust(center)
                    time.sleep(1)
            else:
                self.log_message("❌ 팔레트를 여러 번 조작했지만 원하는 색상이 감지되지 않았습니다.")
                self.running = False
                return

            # 감지 루프 시작
            while self.running:
                sct_img = sct.grab(monitor)
                img = Image.frombytes('RGB', sct_img.size, sct_img.rgb)
                img_np = np.array(img)
                gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)
                circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1, 40,
                                           param1=50, param2=30, minRadius=5, maxRadius=30)
                draw_img = img.copy()
                draw = ImageDraw.Draw(draw_img)

                if circles is not None:
                    circles = np.uint16(np.around(circles))
                    self.log_message(f"{len(circles[0])}개의 원을 찾았습니다.")
                    detected_colors = []
                    for i, (x, y, r) in enumerate(circles[0][:3]):
                        color = tuple(img_np[y, x])
                        hex_color = '#%02x%02x%02x' % color
                        detected_colors.append(color)
                        self.log_message(f"원 {i+1}: 위치 ({x},{y}) 색상 {hex_color}")
                        draw.rectangle([(x-5, y-5), (x+5, y+5)], outline="red", width=2)

                    if must_color:
                        found = any(np.linalg.norm(np.array(must_color) - np.array(dc)) == 0 for dc in detected_colors)
                        if not found:
                            self.log_message("❌ 반드시 포함 색상이 감지되지 않았습니다. 자동화 중단.")
                            self.running = False
                            return

                    if len(detected_colors) == 3:
                        distance = total_color_distance(target_colors, detected_colors)
                        self.log_message(f"총 색상 거리: {distance:.2f}")

                        if distance < self.tolerance.get():
                            self.log_message("🌟 색상이 거의 일치합니다! 자동화를 종료합니다.")
                            self.running = False
                            break
                        else:
                            self.log_message("⏱ 일치하지 않아 팔레트를 조작합니다...")
                            random_adjust(center)
                else:
                    self.log_message("원을 찾지 못했습니다.")

                preview_img = ImageTk.PhotoImage(draw_img.resize((300, 300)))
                self.preview_label.configure(image=preview_img)
                self.preview_label.image = preview_img

                time.sleep(2)

if __name__ == "__main__":
    root = tk.Tk()
    app = DyeToolGUI(root)
    root.mainloop()
