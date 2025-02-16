from ultralytics import YOLO
import cv2
import numpy as np
from pathlib import Path
from collections import defaultdict
import pandas as pd
from typing import Dict, List, Tuple, Set
import json
from sort import Sort  # Simple Online Realtime Tracking
import time


MODEL_PATH = "models/yolov8s_100epochs"


# Get classes from the model
def get_model_classes(model_path):
    model = YOLO(model_path)
    return model.names


class MarineDebrisTracker:
    def __init__(
        self,
        model_path: str,
        confidence_threshold: float = 0.15,
        iou_threshold: float = 0.45,
        max_age: int = 30,
        min_hits: int = 3,
    ):
        """
        Initialize the marine debris tracking system.

        Args:
            model_path: Path to YOLOv8 weights
            confidence_threshold: Minimum detection confidence
            iou_threshold: IOU threshold for NMS
            max_age: Maximum frames to keep track of disappeared objects
            min_hits: Minimum hits to establish a track
        """
        # Load YOLOv8 model
        self.model = YOLO(model_path)

        # Get class names from model
        self.class_names = self.model.names

        # Set model parameters
        self.conf_threshold = confidence_threshold
        self.iou_threshold = iou_threshold

        # Initialize SORT tracker
        self.tracker = Sort(max_age=max_age, min_hits=min_hits)

        # Storage for tracking statistics
        self.tracked_objects = defaultdict(dict)
        self.frame_count = 0
        self.active_tracks = set()
        self.completed_tracks = set()

        # Statistics storage
        self.class_counts = defaultdict(int)
        self.class_areas = defaultdict(list)
        self.spatial_density = defaultdict(list)

    def process_frame(self, frame: np.ndarray) -> Tuple[np.ndarray, Dict]:
        """
        Process a single frame of video.

        Args:
            frame: Input frame (BGR format)

        Returns:
            Annotated frame and detection statistics
        """
        self.frame_count += 1

        # Run YOLOv8 detection
        results = self.model(
            frame,
            conf=self.conf_threshold,
            iou=self.iou_threshold,
        )[0]

        # Extract detections in SORT format [x1,y1,x2,y2,conf]
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

        # Update tracker
        tracked_objects = self.tracker.update(detections)

        # Update statistics and draw annotations
        frame_stats = self._update_tracking_stats(
            frame, detections, tracked_objects, class_ids
        )

        return self._annotate_frame(frame, tracked_objects, class_ids), frame_stats

    def _update_tracking_stats(
        self,
        frame: np.ndarray,
        detections: np.ndarray,
        tracked_objects: np.ndarray,
        class_ids: np.ndarray,
    ) -> Dict:
        """
        Update tracking statistics for the current frame.
        """
        frame_stats = {
            "frame_id": self.frame_count,
            "detections": len(detections),
            "tracked": len(tracked_objects),
            "new_objects": 0,
            "completed_tracks": 0,
            "class_counts": defaultdict(int),
        }

        # Update active tracks
        current_tracks = set()

        for i, track in enumerate(tracked_objects):
            track_id = int(track[4])
            current_tracks.add(track_id)

            # Find matching detection for class information
            if i < len(class_ids):
                class_id = int(class_ids[i])
                class_name = self.class_names[class_id]
                frame_stats["class_counts"][class_name] += 1
            else:
                class_id = -1
                class_name = "unknown"

            if track_id not in self.tracked_objects:
                # New track
                frame_stats["new_objects"] += 1
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

        # Check for completed tracks
        completed = self.active_tracks - current_tracks
        frame_stats["completed_tracks"] = len(completed)

        self.completed_tracks.update(completed)
        self.active_tracks = current_tracks

        return frame_stats

    def _annotate_frame(
        self, frame: np.ndarray, tracked_objects: np.ndarray, class_ids: np.ndarray
    ) -> np.ndarray:
        """
        Draw bounding boxes and tracking information on frame.
        """
        annotated_frame = frame.copy()

        for i, track in enumerate(tracked_objects):
            bbox = track[:4].astype(int)
            track_id = int(track[4])

            # Get class name if available
            class_name = (
                self.class_names[int(class_ids[i])] if i < len(class_ids) else "unknown"
            )

            # Draw bounding box
            cv2.rectangle(
                annotated_frame, (bbox[0], bbox[1]), (bbox[2], bbox[3]), (0, 255, 0), 2
            )

            # Draw ID and class
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

    def generate_report(self) -> Dict:
        """
        Generate a comprehensive analysis report.
        """
        report = {
            "total_frames": self.frame_count,
            "unique_objects": len(self.tracked_objects),
            "completed_tracks": len(self.completed_tracks),
            "track_statistics": [],
            "class_statistics": defaultdict(int),
            "spatial_analysis": {},
        }

        # Analyze each tracked object
        for track_id, track_info in self.tracked_objects.items():
            duration = track_info["last_seen"] - track_info["first_seen"]
            positions = np.array([pos[1] for pos in track_info["positions"]])

            track_stats = {
                "track_id": track_id,
                "class_name": track_info["class_name"],
                "class_id": track_info["class_id"],
                "confidence": track_info["confidence"],
                "duration": duration,
                "avg_size": np.mean((positions[:, 2:] - positions[:, :2]).prod(axis=1)),
                "total_distance": self._calculate_track_distance(positions),
            }

            report["track_statistics"].append(track_stats)
            report["class_statistics"][track_info["class_name"]] += 1

        return report

    def _calculate_track_distance(self, positions: np.ndarray) -> float:
        """
        Calculate total distance traveled by tracked object.
        """
        if len(positions) < 2:
            return 0.0

        # Calculate centers of bounding boxes
        centers = np.column_stack(
            [
                (positions[:, 0] + positions[:, 2]) / 2,
                (positions[:, 1] + positions[:, 3]) / 2,
            ]
        )

        # Calculate total distance
        distances = np.sqrt(np.sum(np.diff(centers, axis=0) ** 2, axis=1))
        return float(np.sum(distances))


def process_video(video_path: str, output_path: str = None, save_report: bool = True):
    """
    Process entire video file and generate analysis.

    Args:
        video_path: Path to input video
        model_path: Path to YOLOv8 weights
        output_path: Path for output video (optional)
        save_report: Whether to save analysis report
    """
    # Initialize tracker
    tracker = MarineDebrisTracker(MODEL_PATH)

    # Open video
    cap = cv2.VideoCapture(video_path)

    # Setup video writer if output path provided
    if output_path:
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = int(cap.get(cv2.CAP_PROP_FPS))

        writer = cv2.VideoWriter(
            output_path, cv2.VideoWriter_fourcc(*"mp4v"), fps, (width, height)
        )

    frame_stats = []
    total_detections = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Process frame
        annotated_frame, stats = tracker.process_frame(frame)
        frame_stats.append(stats)
        total_detections += stats["detections"]

        if output_path:
            writer.write(annotated_frame)

    # Cleanup
    cap.release()
    if output_path:
        writer.release()

    # Generate report
    report = tracker.generate_report()
    report["frame_statistics"] = frame_stats

    # Print summary
    print("\nDetection Summary:")
    print(f"Total frames processed: {tracker.frame_count}")
    print(f"Total individual detections: {total_detections}")
    print(f"Unique tracked objects: {len(tracker.tracked_objects)}")
    print("\nDetections by class:")
    for class_name, count in report["class_statistics"].items():
        print(f"{class_name}: {count} instances")

    return {
        "Total tracked objects": len(tracker.tracked_objects),
        "Class counts:": {
            class_name: count
            for class_name, count in report["class_statistics"].items()
        },
        "Frames processed": tracker.frame_count,
    }


# Example usage
if __name__ == "__main__":
    # Paths would need to be adjusted for your setup
    VIDEO_PATH = "drone.mov"
    # Your TACO-trained YOLOv8 model
    OUTPUT_PATH = "analyzed_footage.mp4"

    report = process_video(VIDEO_PATH, OUTPUT_PATH, save_report=True)

    print(report)
