from ultralytics import YOLO
import cv2
import numpy as np
from pathlib import Path
from collections import defaultdict
import pandas as pd
from typing import Dict, List, Tuple, Set
import json
from sort import Sort  # Simple Online Realtime Tracking for MOT
import time


MODEL_PATH = "models/yolov8s_100epochs.pt"


def get_model_classes(model_path):
    """Get available classes of trash model."""
    model = YOLO(model_path)
    return model.names


class TACOTracker:
    def __init__(
        self,
        model_path: str,
        confidence_threshold: float = 0.15,
        iou_threshold: float = 0.45,
        max_age: int = 30,
        min_hits: int = 3,
    ):
        """
        Initialize the marine debris tracking system."""
        # Load YOLOv8 model
        self.model = YOLO(model_path)

        self.class_names = self.model.names
        self.conf_threshold = confidence_threshold
        self.iou_threshold = iou_threshold

        # Initialize SORT tracker
        self.tracker = Sort(max_age=max_age, min_hits=min_hits)

        # Storage for tracking statistics
        self.tracked_objects = defaultdict(dict)
        self.frame_count = 0

    def process_frame(self, frame: np.ndarray) -> Tuple[np.ndarray, Dict]:
        """
        Process a single frame of video.
        """
        self.frame_count += 1

        # Run inference on YOLOv8.
        results = self.model(
            frame,
            conf=self.conf_threshold,
            iou=self.iou_threshold,
            imgsz=(736, 1280),
            verbose=False,
        )[0]

        # Extract detections and format for SORT.
        detections = []
        class_ids = []
        if len(results.boxes) > 0:
            for box in results.boxes:
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                conf = box.conf[0].cpu().numpy()
                class_id = box.cls[0].cpu().numpy()
                detections.append([x1, y1, x2, y2, conf])
                class_ids.append(class_id)

        detections = np.array(detections) if detections else np.empty((0, 5))
        class_ids = np.array(class_ids) if class_ids else np.array([])

        tracked_objects = self.tracker.update(detections)

        # Draw annotations
        self._update_tracking_stats(tracked_objects, class_ids)

        return self._annotate_frame(frame, tracked_objects, class_ids)

    def _update_tracking_stats(
        self,
        tracked_objects: np.ndarray,
        class_ids: np.ndarray,
    ) -> Dict:
        """
        Update tracking statistics for the current frame.
        """

        # Update active tracks
        current_tracks = set()

        for i, track in enumerate(tracked_objects):
            track_id = int(track[4])
            current_tracks.add(track_id)

            # Find matching detection for class information
            if i < len(class_ids):
                class_id = int(class_ids[i])
                class_name = self.class_names[class_id]
            else:
                class_id = -1
                class_name = "unknown"

            if track_id not in self.tracked_objects:
                # New track
                self.tracked_objects[track_id] = {
                    "first_seen": self.frame_count,
                    "last_seen": self.frame_count,
                    "positions": [(self.frame_count, track[:4])],
                    "class_id": class_id,
                    "class_name": class_name,
                    "confidence": float(track[4]) if len(track) > 4 else 0,
                }
            else:
                # Update existing track
                self.tracked_objects[track_id]["last_seen"] = self.frame_count
                self.tracked_objects[track_id]["positions"].append(
                    (self.frame_count, track[:4])
                )

    def _annotate_frame(
        self, frame: np.ndarray, tracked_objects: np.ndarray, class_ids: np.ndarray
    ) -> np.ndarray:
        """
        Draw bounding boxes and class on frame.
        """
        annotated_frame = frame.copy()

        for i, track in enumerate(tracked_objects):
            bbox = track[:4].astype(int)
            track_id = int(track[4])

            class_name = (
                self.class_names[int(class_ids[i])] if i < len(class_ids) else "unknown"
            )

            cv2.rectangle(
                annotated_frame, (bbox[0], bbox[1]), (bbox[2], bbox[3]), (0, 255, 0), 2
            )

            label = f"ID: {track_id} | {class_name}"
            cv2.putText(
                annotated_frame,
                label,
                (bbox[0], bbox[1] - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 255, 0),
                2,
            )

        return annotated_frame

    def _calculate_track_distance(self, positions: np.ndarray) -> float:
        """
        Calculate total distance traveled by tracked object.
        """
        if len(positions) < 2:
            return 0.0

        # Calculate bounding box centers
        centers = np.column_stack(
            [
                (positions[:, 0] + positions[:, 2]) / 2,
                (positions[:, 1] + positions[:, 3]) / 2,
            ]
        )

        # Calculate total distance
        distances = np.sqrt(np.sum(np.diff(centers, axis=0) ** 2, axis=1))
        return float(np.sum(distances))

    def frequency_counts(self) -> Dict:
        """
        Generate frequency counts for each class.
        """
        report = defaultdict(int)

        # Analyze each tracked object
        for _, track_info in self.tracked_objects.items():
            report[track_info["class_name"]] += 1

        return report


def process_video(video_path: str, output_path: str) -> dict:
    """
    Process entire video file and write annotated video to filesystem. Output statistics.
    """
    # Initialize object tracking
    tracker = TACOTracker(MODEL_PATH)

    # Load video
    cap = cv2.VideoCapture(video_path)

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))

    writer = cv2.VideoWriter(
        output_path, cv2.VideoWriter_fourcc(*"mp4v"), fps, (width, height)
    )

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        annotated_frame = tracker.process_frame(frame)

        if output_path:
            writer.write(annotated_frame)

    # Cleanup cv2 objects
    cap.release()
    if output_path:
        writer.release()

    report = tracker.frequency_counts()

    return {
        "Total tracked objects": len(tracker.tracked_objects),
        "Class counts:": {class_name: count for class_name, count in report.items()},
        "Frames processed": tracker.frame_count,
    }


if __name__ == "__main__":

    # Path to input video
    VIDEO_PATH = "drone_sample.mov"

    # Path to output video with annotations
    OUTPUT_PATH = "annotations.mp4"

    report = process_video(VIDEO_PATH, OUTPUT_PATH)

    print(report)
