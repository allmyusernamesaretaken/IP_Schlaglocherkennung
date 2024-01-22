# image_utils.py
import cv2
import supervision as sv
import numpy as np


def save_image(image, output_path):
    # Save the image to the specified path
    cv2.imwrite(output_path, image)


def label_image(frame,detections, model_names):
    ZONE_POLYGON = np.array([
        [0, 0],
        [0, 0],
        [0, 0],
        [0, 0]
    ])

    box_annotator = sv.BoxAnnotator(
        thickness=2,
        text_thickness=2,
        text_scale=1
    )

    zone_polygon = (ZONE_POLYGON * np.array([1280, 720])).astype(int)
    zone = sv.PolygonZone(polygon=zone_polygon, frame_resolution_wh=tuple([1280, 720]))
    zone_annotator = sv.PolygonZoneAnnotator(
        zone=zone,
        color=sv.Color.red(),
        thickness=2,
        text_thickness=4,
        text_scale=2
    )

    labels = [
        f"{model_names[class_id]} {confidence:0.2f}"
        for _, _, confidence, class_id, _ in detections
    ]
    frame = box_annotator.annotate(
        scene=frame,
        detections=detections,
        labels=labels
    )

    zone.trigger(detections=detections)
    return zone_annotator.annotate(scene=frame)
