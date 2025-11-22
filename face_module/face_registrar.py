import cv2
import face_recognition
import os
from datetime import datetime
from typing import Optional, Tuple
import numpy as np


class FaceRegistrar:
    """Handles face registration for new people."""

    def __init__(self, image_dir: str = "data/face_images"):
        """
        Initialize face registrar.

        Args:
            image_dir: Directory to save face images
        """
        self.image_dir = image_dir
        os.makedirs(image_dir, exist_ok=True)

    def capture_face_from_webcam(self, name: str, show_preview: bool = True) -> Tuple[Optional[np.ndarray], Optional[str]]:
        """
        Capture face image from webcam.

        Args:
            name: Person's name
            show_preview: Whether to show preview window

        Returns:
            Tuple of (face_encoding, image_path) or (None, None) if failed
        """
        print(f"\nCapturing face for {name}...")
        print("Instructions:")
        print("- Look directly at the camera")
        print("- Ensure good lighting")
        print("- Press SPACE to capture")
        print("- Press ESC to cancel")

        cap = cv2.VideoCapture(0)

        if not cap.isOpened():
            print("Error: Could not open webcam!")
            return None, None

        captured_encoding = None
        image_path = None

        while True:
            ret, frame = cap.read()
            if not ret:
                print("Error: Failed to capture frame!")
                break

            # Display frame
            display_frame = frame.copy()

            # Detect faces in the frame
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            face_locations = face_recognition.face_locations(rgb_frame)

            # Draw rectangles around faces
            for (top, right, bottom, left) in face_locations:
                cv2.rectangle(display_frame, (left, top), (right, bottom), (0, 255, 0), 2)
                cv2.putText(display_frame, "Face Detected", (left, top - 10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            # Show instructions
            cv2.putText(display_frame, "SPACE: Capture | ESC: Cancel", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

            if show_preview:
                cv2.imshow('Register Face', display_frame)

            key = cv2.waitKey(1) & 0xFF

            # Capture on SPACE
            if key == ord(' '):
                if len(face_locations) == 0:
                    print("No face detected! Please try again.")
                    continue
                elif len(face_locations) > 1:
                    print("Multiple faces detected! Please ensure only one person is in frame.")
                    continue

                # Encode the face
                face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

                if len(face_encodings) > 0:
                    captured_encoding = face_encodings[0]

                    # Save the image
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    image_filename = f"{name.replace(' ', '_')}_{timestamp}.jpg"
                    image_path = os.path.join(self.image_dir, image_filename)
                    cv2.imwrite(image_path, frame)

                    print(f"Face captured successfully!")
                    print(f"Image saved to: {image_path}")
                    break
                else:
                    print("Failed to encode face! Please try again.")

            # Cancel on ESC
            elif key == 27:
                print("Capture cancelled.")
                break

        cap.release()
        cv2.destroyAllWindows()

        return captured_encoding, image_path

    def load_face_from_image(self, image_path: str) -> Optional[np.ndarray]:
        """
        Load and encode face from an image file.

        Args:
            image_path: Path to the image file

        Returns:
            Face encoding or None if failed
        """
        if not os.path.exists(image_path):
            print(f"Error: Image file not found: {image_path}")
            return None

        try:
            # Load image
            image = face_recognition.load_image_file(image_path)

            # Detect faces
            face_locations = face_recognition.face_locations(image)

            if len(face_locations) == 0:
                print("Error: No face detected in the image!")
                return None
            elif len(face_locations) > 1:
                print("Warning: Multiple faces detected! Using the first one.")

            # Encode face
            face_encodings = face_recognition.face_encodings(image, face_locations)

            if len(face_encodings) > 0:
                print("Face loaded and encoded successfully!")
                return face_encodings[0]
            else:
                print("Error: Failed to encode face!")
                return None

        except Exception as e:
            print(f"Error loading image: {e}")
            return None
