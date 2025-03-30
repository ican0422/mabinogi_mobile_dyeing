# import cv2
# import numpy as np

# def detect_tone_regions(img_np):
#     """
#     좌/중/우 영역으로 나눠서 밝기(V)와 채도(S) 기준으로 톤 감지
#     - 어두움: V < 80
#     - 밝음: V > 180
#     - 중간: 그 사이
#     단, 채도(S) 낮으면 무채색 계열로 간주
#     """
#     h, w, _ = img_np.shape
#     region_width = w // 3
#     tones = []

#     print("[DEBUG] === 톤 분석 시작 ===")
#     for i in range(3):
#         region = img_np[:, i * region_width:(i + 1) * region_width]
#         hsv = cv2.cvtColor(region, cv2.COLOR_RGB2HSV)
#         h_, s, v = cv2.split(hsv)

#         mean_h = np.mean(h_)
#         mean_s = np.mean(s)
#         mean_v = np.mean(v)

#         if mean_s < 40:
#             tone = "무채색"
#         elif mean_v < 80:
#             tone = "어두움"
#         elif mean_v > 180:
#             tone = "밝음"
#         else:
#             tone = "중간"

#         tone_info = {
#             "hue": mean_h,
#             "saturation": mean_s,
#             "value": mean_v,
#             "tone": tone
#         }
#         tones.append(tone_info)

#         print(f"[영역 {i+1}] 톤: {tone} | 색상(H): {mean_h:.2f} | 채도(S): {mean_s:.2f} | 명도(V): {mean_v:.2f}")
#     print("[DEBUG] === 톤 분석 종료 ===")

#     return tones
