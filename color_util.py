from typing import Tuple


def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
    """HEX 문자열을 RGB 튜플로 변환"""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def rgb_to_hex(rgb: Tuple[int, int, int]) -> str:
    """RGB 튜플을 HEX 문자열로 변환"""
    return '#%02x%02x%02x' % rgb


def color_distance(c1: Tuple[int, int, int], c2: Tuple[int, int, int]) -> float:
    """두 RGB 색상 간의 유클리디언 거리 계산"""
    return ((c1[0] - c2[0]) ** 2 +
            (c1[1] - c2[1]) ** 2 +
            (c1[2] - c2[2]) ** 2) ** 0.5


def total_color_distance(target_colors: list, current_colors: list) -> float:
    """
    입력된 목표 색상 3개와 현재 감지된 색상 3개 간의 총 거리 합을 계산
    순서대로 비교됨
    """
    return sum(color_distance(t, c) for t, c in zip(target_colors, current_colors))
