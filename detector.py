from collections import Counter
from typing import List, Tuple
import numpy as np
from sklearn.cluster import KMeans


def extract_dominant_colors(image_np: np.ndarray, k: int = 10) -> List[Tuple[int, int, int]]:
    """
    이미지에서 가장 많이 쓰인 RGB 색상 K개 추출
    """
    pixels = image_np.reshape((-1, 3))
    kmeans = KMeans(n_clusters=k, n_init='auto', random_state=42).fit(pixels)
    centers = kmeans.cluster_centers_.astype(int)
    return [tuple(color) for color in centers]

def contains_all_target_colors(dominants: List[Tuple[int, int, int]], targets: List[Tuple[int, int, int]], threshold: float = 30.0) -> bool:
    """
    dominant 컬러 리스트에 target 컬러들이 모두 비슷하게 포함되어 있는지 판단
    """
    def color_distance(c1, c2):
        return ((c1[0]-c2[0])**2 + (c1[1]-c2[1])**2 + (c1[2]-c2[2])**2) ** 0.5

    for target in targets:
        if not any(color_distance(target, d) < threshold for d in dominants):
            return False
    return True