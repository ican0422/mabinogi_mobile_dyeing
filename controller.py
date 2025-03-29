import pyautogui
import random
import time

# 팔레트 조작을 위한 유틸리티 모듈


def drag_palette(from_pos, to_pos, duration=0.3):
    """
    팔레트를 클릭해서 드래그 이동하는 함수
    from_pos: 시작 위치 (x, y)
    to_pos: 끝 위치 (x, y)
    """
    pyautogui.moveTo(from_pos[0], from_pos[1], duration=0.2)
    pyautogui.mouseDown(button='left')
    pyautogui.moveTo(to_pos[0], to_pos[1], duration=duration)
    pyautogui.mouseUp()


def rotate_palette(center, angle_deg=15):
    """
    팔레트를 우클릭 기준으로 회전시키는 함수
    center: 회전 중심 좌표 (x, y)
    angle_deg: 회전 정도 (양수는 시계방향)
    """
    pyautogui.moveTo(center[0], center[1], duration=0.2)
    pyautogui.mouseDown(button='right')
    offset = 50 if angle_deg > 0 else -50
    pyautogui.moveRel(offset, 0, duration=0.3)
    pyautogui.mouseUp()


def zoom_palette(center, direction='in'):
    """
    마우스 휠을 이용한 팔레트 확대/축소
    direction: 'in' → 확대 / 'out' → 축소
    """
    pyautogui.moveTo(center[0], center[1], duration=0.1)
    if direction == 'in':
        pyautogui.scroll(200)
    else:
        pyautogui.scroll(-200)


def random_adjust(center):
    """
    팔레트를 랜덤하게 회전, 이동, 확대 중 하나 수행 (탐색 목적)
    """
    action = random.choice(['rotate', 'drag', 'zoom'])
    if action == 'rotate':
        rotate_palette(center, angle_deg=random.choice([-20, 20]))
    elif action == 'drag':
        dx = random.randint(-40, 40)
        dy = random.randint(-40, 40)
        drag_palette(center, (center[0]+dx, center[1]+dy))
    elif action == 'zoom':
        zoom_palette(center, direction=random.choice(['in', 'out']))
    time.sleep(1)
