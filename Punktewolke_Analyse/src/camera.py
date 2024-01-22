import cv2 as cv


class Camera:

    def __init__(self, source=0, width=1920, height=1080):
        self.camera = cv.VideoCapture(source)
        if not self.camera.isOpened():
            raise ValueError("Unable to open camera!")
        self.camera.set(cv.CAP_PROP_FRAME_WIDTH, width)
        self.camera.set(cv.CAP_PROP_FRAME_HEIGHT, height)
        self.width = self.camera.get(cv.CAP_PROP_FRAME_WIDTH)
        self.height = self.camera.get(cv.CAP_PROP_FRAME_HEIGHT)

    def __del__(self):
        if self.camera.isOpened():
            self.camera.release()

    def get_frame(self):
        if self.camera.isOpened():
            ret, frame = self.camera.read()

            if ret:
                return frame
            else:
                return None
        else:
            return None
