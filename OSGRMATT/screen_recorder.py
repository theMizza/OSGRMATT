from pathlib import Path
from threading import Thread
from typing import Optional
import cv2
import numpy as np
from time import sleep
import logging

logger = logging.getLogger(__name__)


class Recorder:
    def __init__(self, driver, wait_time: float):
        self._driver = driver
        self._wait_time = wait_time  # time between frames
        self._video_th = None
        self._video_process = False
        self.video_file: Optional[Path] = None
        self.BASE_DIR = Path(__file__).parent.resolve()

    def start_video_rec(self, filename):
        logger.info("Start screencast record")
        self._video_process = True
        self.video_file = Path(filename)
        self.video_file.unlink(missing_ok=True)
        self._video_th = Thread(target=self._video_record, name="video_record", daemon=True)
        self._video_th.start()

    def stop_video_rec(self):
        logger.info("Stop screencast record")
        if self._video_th:
            self._video_process = False
            self._video_th.join()

    def _video_record(self):
        def _get_screen():
            self._driver.get_screenshot_as_file(f"{self.BASE_DIR}/tmp/screenshots/last.png")
            return cv2.imread(f"{self.BASE_DIR}/tmp/screenshots/last.png")

        image = _get_screen()
        start_height, start_width, layers = image.shape

        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(str(self.video_file), fourcc, 1.0, (start_width, start_height))
        try:
            while self._video_process:
                image = _get_screen()
                height, width, layers = image.shape
                if (height, width) != (start_height, start_width):
                    blank = np.zeros((start_height, start_width, 3), np.uint8)
                    blank[:, :] = (220, 220, 220)
                    new_img = blank.copy()
                    new_img[0:0 + height, 0:0 + width] = image.copy()
                    image = new_img
                out.write(image)

                sleep(self._wait_time)
        finally:
            out.release()
            cv2.destroyAllWindows()
