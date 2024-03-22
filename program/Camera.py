import numpy as np
import cv2
import posix_ipc
import mmap
from jetcam.csi_camera import CSICamera
from jetcam.utils import bgr8_to_jpeg

TARGET_WIDTH = 224
TARGET_HEIGHT = 224
TARGET_DEPTH = 3

class Camera:
    def __init__(self):
        sample_array = np.zeros((TARGET_HEIGHT, TARGET_WIDTH, TARGET_DEPTH), dtype=np.uint8)
        self.shared_memory_name = "jetson"
        self.memory = posix_ipc.SharedMemory(self.shared_memory_name, posix_ipc.O_CREAT, size=sample_array.nbytes)
        self.map_file = mmap.mmap(self.memory.fd, self.memory.size)
        # Immediately close the file descriptor since we don't need it anymore
        self._camera = CSICamera(width=224, height=224)

    def run_camera(self):
        self._camera.running = True
        self._camera.observe(self.update_image, names='value')

    def update_image(self, change):
        image = change['new']
        shared_a = np.ndarray(image.shape, dtype=image.dtype, buffer=self.map_file)
        np.copyto(shared_a, image)

    def unlink_shared_memory(self):
        self.map_file.close()
        self.memory.unlink()

if __name__ == '__main__':
    camera = Camera()
    camera.run_camera()
