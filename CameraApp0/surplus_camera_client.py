import json
import logging
import numpy as np
import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

default_camera_url = "http://127.0.0.1:8080"
deafult_image_width = 1280
default_image_height = 720
frame_rate = 10


class SurplusCameraClient:

    client = None

    def __init__(self, url):
        self.url = url
        state = self._get_camera_state()
        self.width = state["width"]
        self.height = state["height"]
        self.camera_running = state["capturing"]
        if not self.camera_running:
            self._start_capture()

    def _get_camera_state(self):
        return requests.get(self.url + "/v1/cameraState").json()

    @classmethod
    def get_client(cls, url=default_camera_url):
        if not cls.client:
            cls.client = cls(url)
        return cls.client

    def _start_capture(self):
        if self.camera_running:
            logging.warn("Camera is already running. skipping.")
            return
        response = requests.get(self.url + "/v1/startCameraCapture")
        if response.status_code != 200:
            return False
        self.camera_running = 1
        logger.info("Camera has been started.")

    def _stop_capture(self):
        if not self.camera_running:
            logging.warn("Camera is not running. skipping.")
            return
        response = requests.get(self.url + "/v1/stopCameraCapture")
        if response.status_code != 200:
            return False
        self.camera_running = 0
        logger.info("Camera has been stopped.")

    def set_capture_size(self, width, height):
        self._stop_capture()

        camera_state = {"width": width, "height": height, "framerate": frame_rate}
        print(camera_state)
        try:
            response = requests.patch(
                self.url + "/v1/cameraState", json.dumps(camera_state)
            )
            print(response)
            if response.status_code != 200:
                logger.error("Failed to configure capture size." + response.text)
        except Exception as e:
            print(e)
            logger.error("Failed to configure capture size.")
        finally:
            self.width = width
            self.height = height

        self._start_capture()

    def capture_image(self):
        if not self.camera_running:
            logger.error("Camera is not running.")
            return

        response = requests.get(self.url + "/v1/cameraImage")
        if response.status_code != 200:
            logger.error("Failed to capture image.")
            return

        return response.content

    def capture_image_as_nparray(self):
        buffer = self.capture_image()
        frame = np.frombuffer(buffer, np.uint8).reshape(self.height, self.width, 3)
        return frame

