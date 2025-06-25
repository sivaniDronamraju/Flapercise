import cv2
import mediapipe as mp

class JumpDetector:
    def __init__(self, threshold=0.03, camera_index=0):
        self.previous_hip_y = None
        self.threshold = threshold
        self.cap = cv2.VideoCapture(camera_index)

        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose()
        self.mp_drawing = mp.solutions.drawing_utils  

    def detect_start_gesture(self):
        image_rgb, frame = self.get_frame()
        if image_rgb is None:
            return False, frame

        results = self.pose.process(image_rgb)
        start_detected = False

        if results.pose_landmarks:
            self.mp_drawing.draw_landmarks(
                frame,
                results.pose_landmarks,
                self.mp_pose.POSE_CONNECTIONS
            )

            right_wrist = results.pose_landmarks.landmark[self.mp_pose.PoseLandmark.RIGHT_WRIST]
            right_shoulder = results.pose_landmarks.landmark[self.mp_pose.PoseLandmark.RIGHT_SHOULDER]

            if right_wrist.y < right_shoulder.y:
                start_detected = True

        return start_detected, frame


    def get_frame(self):
        success, frame = self.cap.read()
        if not success:
            return None, False

        frame = cv2.flip(frame, 1)
        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        return image_rgb, frame

    def detect_jump(self):
        image_rgb, frame = self.get_frame()
        if image_rgb is None:
            return False, frame

        results = self.pose.process(image_rgb)
        jump_detected = False

        if results.pose_landmarks:
            self.mp_drawing.draw_landmarks(
                frame,
                results.pose_landmarks,
                self.mp_pose.POSE_CONNECTIONS
            )

            # Check hip movement
            left_hip = results.pose_landmarks.landmark[self.mp_pose.PoseLandmark.LEFT_HIP]
            current_hip_y = left_hip.y

            print(f"Hip Y: {current_hip_y:.4f}")

            if self.previous_hip_y is not None:
                if self.previous_hip_y - current_hip_y > self.threshold:
                    jump_detected = True

            self.previous_hip_y = current_hip_y

        return jump_detected, frame


    def release(self):
        self.cap.release()
        cv2.destroyAllWindows()
