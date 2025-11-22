import cv2
import face_recognition
import numpy as np
from typing import List, Tuple, Dict, Callable
from datetime import datetime


class FaceRecognizer:
    """Handles real-time face recognition from webcam."""

    def __init__(self, known_faces: List[Tuple[int, str, np.ndarray]], tolerance: float = 0.6):
        """
        Initialize face recognizer.

        Args:
            known_faces: List of tuples (person_id, name, face_encoding)
            tolerance: Face recognition tolerance (lower is more strict)
        """
        self.known_face_encodings = [face[2] for face in known_faces]
        self.known_face_ids = [face[0] for face in known_faces]
        self.known_face_names = [face[1] for face in known_faces]
        self.tolerance = tolerance
        self.recognized_today = set()

    def recognize_faces_from_webcam(self, on_recognition: Callable[[int, str], None] = None,
                                    process_every_n_frames: int = 2) -> None:
        """
        Start real-time face recognition from webcam.

        Args:
            on_recognition: Callback function called when a face is recognized (person_id, name)
            process_every_n_frames: Process every N frames for better performance
        """
        print("\nStarting webcam face recognition...")
        print("Instructions:")
        print("- Press 'q' or ESC to quit")
        print("- Recognized faces will be marked with green boxes")
        print("- Unknown faces will be marked with red boxes")
        print()

        cap = cv2.VideoCapture(0)

        if not cap.isOpened():
            print("Error: Could not open webcam!")
            return

        frame_count = 0

        while True:
            ret, frame = cap.read()
            if not ret:
                print("Error: Failed to capture frame!")
                break

            frame_count += 1

            # Process every N frames to improve performance
            if frame_count % process_every_n_frames == 0:
                # Resize frame for faster processing
                small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
                rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

                # Detect faces
                face_locations = face_recognition.face_locations(rgb_small_frame)
                face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

                # Process each detected face
                for face_encoding, face_location in zip(face_encodings, face_locations):
                    # Compare with known faces
                    matches = face_recognition.compare_faces(
                        self.known_face_encodings,
                        face_encoding,
                        tolerance=self.tolerance
                    )

                    name = "Unknown"
                    person_id = None
                    color = (0, 0, 255)  # Red for unknown

                    # Use the known face with the smallest distance
                    if len(self.known_face_encodings) > 0:
                        face_distances = face_recognition.face_distance(
                            self.known_face_encodings,
                            face_encoding
                        )

                        best_match_index = np.argmin(face_distances)

                        if matches[best_match_index]:
                            name = self.known_face_names[best_match_index]
                            person_id = self.known_face_ids[best_match_index]
                            color = (0, 255, 0)  # Green for recognized

                            # Call recognition callback
                            if on_recognition and person_id not in self.recognized_today:
                                on_recognition(person_id, name)
                                self.recognized_today.add(person_id)
                                print(f"✓ Recognized: {name} at {datetime.now().strftime('%H:%M:%S')}")

                    # Scale back up face locations
                    top, right, bottom, left = face_location
                    top *= 4
                    right *= 4
                    bottom *= 4
                    left *= 4

                    # Draw rectangle around face
                    cv2.rectangle(frame, (left, top), (right, bottom), color, 2)

                    # Draw label
                    cv2.rectangle(frame, (left, bottom - 35), (right, bottom), color, cv2.FILLED)
                    cv2.putText(frame, name, (left + 6, bottom - 6),
                               cv2.FONT_HERSHEY_DUPLEX, 0.6, (255, 255, 255), 1)

            # Show stats
            cv2.putText(frame, f"Recognized Today: {len(self.recognized_today)}", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.putText(frame, "Press 'q' or ESC to quit", (10, 60),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

            # Display frame
            cv2.imshow('Attendance System - Face Recognition', frame)

            # Check for quit
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q') or key == 27:
                print("\nStopping recognition...")
                break

        cap.release()
        cv2.destroyAllWindows()
        print(f"\nSession complete. Total recognized: {len(self.recognized_today)}")

    def recognize_face_from_frame(self, frame: np.ndarray) -> List[Dict]:
        """
        Recognize faces in a single frame.

        Args:
            frame: Image frame (BGR format)

        Returns:
            List of recognized faces with their information
        """
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Detect faces
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        results = []

        for face_encoding, face_location in zip(face_encodings, face_locations):
            # Compare with known faces
            matches = face_recognition.compare_faces(
                self.known_face_encodings,
                face_encoding,
                tolerance=self.tolerance
            )

            name = "Unknown"
            person_id = None
            confidence = 0.0

            if len(self.known_face_encodings) > 0:
                face_distances = face_recognition.face_distance(
                    self.known_face_encodings,
                    face_encoding
                )

                best_match_index = np.argmin(face_distances)

                if matches[best_match_index]:
                    name = self.known_face_names[best_match_index]
                    person_id = self.known_face_ids[best_match_index]
                    confidence = 1 - face_distances[best_match_index]

            results.append({
                'person_id': person_id,
                'name': name,
                'location': face_location,
                'confidence': confidence
            })

        return results

    def reset_recognition_cache(self):
        """Reset the cache of recognized faces for the day."""
        self.recognized_today.clear()

    def update_known_faces(self, known_faces: List[Tuple[int, str, np.ndarray]]):
        """
        Update the list of known faces.

        Args:
            known_faces: List of tuples (person_id, name, face_encoding)
        """
        self.known_face_encodings = [face[2] for face in known_faces]
        self.known_face_ids = [face[0] for face in known_faces]
        self.known_face_names = [face[1] for face in known_faces]
