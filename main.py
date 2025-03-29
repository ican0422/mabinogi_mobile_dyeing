import tkinter as tk
from tkinter import messagebox
import pyautogui
import threading
import time
import mss
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageTk
from color_util import hex_to_rgb, total_color_distance
from controller import random_adjust
from detector import extract_dominant_colors, contains_all_target_colors

VERSION = "염색도우미 v1.0.0"

class DyeToolGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("염색 자동화 도우미")

        version_label = tk.Label(root, text=VERSION, fg='gray')
        version_label.pack(pady=(5, 0))

        self.hex_vars = [tk.StringVar(value="#000000"),
                         tk.StringVar(value="#FFFFFF"),
                         tk.StringVar(value="#FFE400")]

        tk.Label(root, text="원하는 색상 3가지를 입력하세요 (Hex)").pack()
        for i in range(3):
            tk.Entry(root, textvariable=self.hex_vars[i]).pack()

        self.tolerance = tk.IntVar(value=50)
        tk.Label(root, text="허용 오차 (정확도 기준)").pack()
        scale_frame = tk.Frame(root)
        scale_frame.pack(pady=5)
        tk.Scale(scale_frame, from_=0, to=100, orient='horizontal', variable=self.tolerance).pack(side=tk.LEFT)
        self.tolerance_entry = tk.Entry(scale_frame, textvariable=self.tolerance, width=5)
        self.tolerance_entry.pack(side=tk.LEFT, padx=5)

        tk.Button(root, text="팔레트 영역 지정하기", command=self.select_region).pack(pady=5)
        tk.Button(root, text="자동 인식 시작", command=self.start_detection).pack(pady=5)
        tk.Button(root, text="정지", command=self.stop_detection).pack(pady=5)

        self.log = tk.Text(root, height=10, width=50)
        self.log.pack(pady=10)

        self.preview_label = tk.Label(root)
        self.preview_label.pack(pady=5)

        self.region = None
        self.running = False

    def log_message(self, msg):
        self.log.insert(tk.END, f"{msg}\n")
        self.log.see(tk.END)

    def select_region(self):
        self.log_message("3초 후 시작 좌표를 가져옵니다. 마우스를 원하는 위치에 대세요.")
        time.sleep(3)
        x1, y1 = pyautogui.position()
        self.log_message(f"시작 좌표: ({x1}, {y1})")

        self.log_message("3초 후 끝 좌표를 가져옵니다. 마우스를 대고 기다리세요.")
        time.sleep(3)
        x2, y2 = pyautogui.position()
        self.log_message(f"끝 좌표: ({x2}, {y2})")

        left = min(x1, x2)
        top = min(y1, y2)
        width = abs(x2 - x1)
        height = abs(y2 - y1)

        self.region = (left, top, width, height)
        self.log_message(f"영역이 설정되었습니다: {self.region}")

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
            target_colors = [hex_to_rgb(var.get()) for var in self.hex_vars]
            center = (self.region[0] + self.region[2] // 2, self.region[1] + self.region[3] // 2)

            # 팔레트 존재 색상 사전 검사 (최초 1회)
            sct_img = sct.grab(monitor)
            img = Image.frombytes('RGB', sct_img.size, sct_img.rgb)
            img_np = np.array(img)
            dominants = extract_dominant_colors(img_np)
            if not contains_all_target_colors(dominants, target_colors, threshold=self.tolerance.get()):
                self.log_message("❌ 팔레트에 입력한 색상 중 일부가 존재하지 않습니다. 조합 불가.")
                self.running = False
                return

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

                    if len(detected_colors) == 3:
                        distance = total_color_distance(target_colors, detected_colors)
                        self.log_message(f"총 색상 거리: {distance:.2f}")

                        if distance < self.tolerance.get():
                            self.log_message("🎯 색상이 거의 일치합니다! 자동화를 종료합니다.")
                            self.running = False
                            break
                        else:
                            self.log_message("⏱ 일치하지 않아 팔레트를 조작합니다...")
                            random_adjust(center)
                else:
                    self.log_message("원을 찾지 못했습니다.")

                # 시각화 이미지 표시
                preview_img = ImageTk.PhotoImage(draw_img.resize((300, 300)))
                self.preview_label.configure(image=preview_img)
                self.preview_label.image = preview_img

                time.sleep(2)

if __name__ == "__main__":
    root = tk.Tk()
    app = DyeToolGUI(root)
    root.mainloop()
