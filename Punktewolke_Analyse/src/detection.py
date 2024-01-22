from ultralytics import YOLO
import supervision as sv


class Detection:
    def __init__(self, path_to_weights):
        self.model = YOLO(path_to_weights)

    def detect_potholes(self, frame):
        result = self.model.predict(frame)[0]
        return sv.Detections.from_ultralytics(result)