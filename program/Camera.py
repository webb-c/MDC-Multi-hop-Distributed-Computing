from multiprocessing import shared_memory
import numpy as np
import cv2
from jetcam.csi_camera import CSICamera
from jetcam.utils import bgr8_to_jpeg

TARGET_WIDTH = 224
TAREGET_HEIGHT= 224
TARGET_DEPTH = 3

class Camera:
    def __init__(self):
        sample_array = np.zeros((TAREGET_HEIGHT, TARGET_WIDTH, TARGET_DEPTH), dtype=np.uint8)  # (600768,)
        self._shared_memory = shared_memory.SharedMemory(name ='shm',create=True, size=sample_array.nbytes)
        self._camera = CSICamera(width=224, height=224)

    def run_camera(self):
        self._camera.running = True
        self._camera.observe(self.update_image, names='value')

    def update_image(self, change):
        image = change['new']
        shared_a = np.ndarray(image.shape, dtype=image.dtype, buffer=self._shared_memory.buf)
        shared_a[:] = image

    def unlink_shared_memory(self):
        self._shared_memory.unlink()
        self._shared_memory.close()

if __name__ == '__main__':
    camera = Camera()