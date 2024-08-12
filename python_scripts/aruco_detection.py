import cv2
from cv2 import aruco
import numpy as np

class aruco_detection:
    def __init__(self):
        self.marker_dict = aruco.Dictionary_get(aruco.DICT_4X4_50)
        self.param_markers = aruco.DetectorParameters_create()
    def main_loop(self, img, settings):

        gray_frame = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        marker_corners, marker_IDs, reject = aruco.detectMarkers(
            gray_frame, self.marker_dict, parameters=self.param_markers
        )
        list_of_markers = []
        if marker_corners:
            for ids, corners in zip(marker_IDs, marker_corners):
                cv2.polylines(
                    img, [corners.astype(np.int32)], True, (0, 0, 255), 2, cv2.LINE_AA
                )
                corners = corners.reshape(4, 2)
                corners = corners.astype(int)
                top_right = corners[0].ravel()
                top_left = corners[1].ravel()
                bottom_right = corners[2].ravel()
                bottom_left = corners[3].ravel()
                cv2.putText(
                    img,
                    f"id: {ids[0]}",
                    top_right,
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1.3,
                    (0, 255, 0),
                    2,
                    cv2.LINE_AA,
                )
                list_of_markers.append([ids, corners])
        settings.set_img(img)
        return img, list_of_markers
