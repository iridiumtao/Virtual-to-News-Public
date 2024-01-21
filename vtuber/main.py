"""
Main program to run the detection
EX：python main.py --connect -m file -v ./face_video.mp4

Help:
```
python main.py -h 
```
"""

import csv
# for TCP connection with unity
import socket
from argparse import ArgumentParser
from collections import deque
from pathlib import Path
from platform import system

import cv2
import mediapipe as mp
import numpy as np
# Miscellaneous detections (eyes/ mouth...)
from facial_features import Eyes, FacialFeatures
# face detection and facial landmark
from facial_landmark import FaceMeshDetector
# pose estimation and stablization
from pose_estimator import PoseEstimator
from stabilizer import Stabilizer


def get_video_duration(cap):
    # cap = cv2.VideoCapture(filename)
    if cap.isOpened():
        rate = cap.get(5)
        frame_num = cap.get(7)
        duration = frame_num / rate
        return duration
    return -1


# init TCP connection with unity
# return the socket connected
def init_TCP(host, port):
    address = (host, port)
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(address)
        return s
    except ConnectionRefusedError:
        exit(
            '1. You need start Unity and run play mode first\n2. Check host and port set correctly\n3. Network settings are abnormal'
        )


def send_info_to_unity(s, args):
    msg = '%.4f ' * len(args) % args
    s.send(bytes(msg, "utf-8"))


def print_debug_msg(args):
    msg = '%.4f ' * len(args) % args
    print(msg)


def main():
    # 相機或是影片
    if args.mode is None:
        raise ValueError("未指定來源 -m {cam|file}")

    if args.mode == "file":
        print(f"filepath: {args.file_path}")
        filename = Path(args.file_path)
        if not filename.exists():
            raise FileNotFoundError(str(filename.absolute()))

        cap = cv2.VideoCapture(str(filename))
        duration = np.float64(get_video_duration(cap))

    if args.mode == "cam":
        duration = 60
        cap = cv2.VideoCapture(args.cam)

    # Facemesh
    detector = FaceMeshDetector()

    # get a sample frame for pose estimation img
    success, img = cap.read()

    # Pose estimation related
    pose_estimator = PoseEstimator((img.shape[0], img.shape[1]))
    image_points = np.zeros((pose_estimator.model_points_full.shape[0], 2))

    # extra 10 points due to new attention model (in iris detection)
    iris_image_points = np.zeros((10, 2))

    # Introduce scalar stabilizers for pose.
    pose_stabilizers = [
        Stabilizer(state_num=2, measure_num=1, cov_process=0.1, cov_measure=0.1) for _ in range(6)
    ]

    # for eyes
    eyes_stabilizers = [
        Stabilizer(state_num=2, measure_num=1, cov_process=0.1, cov_measure=0.1) for _ in range(6)
    ]

    # for mouth_dist
    mouth_dist_stabilizer = Stabilizer(state_num=2, measure_num=1, cov_process=0.1, cov_measure=0.1)

    # Initialize TCP connection
    if args.connect:
        socket = init_TCP(args.host, args.port)

    play = 1

    while cap.isOpened():
        if (play):
            success, img = cap.read()

            if not success:
                print("Video send has ended")
                break

            # Pose estimation by 3 steps:
            # 1. detect face;
            # 2. detect landmarks;
            # 3. estimate pose

            # first two steps
            img_facemesh, faces = detector.findFaceMesh(img)

            # flip the input image so that it matches the facemesh stuff
            img = cv2.flip(img, 1)

            # if there is any face detected
            if faces:
                # only get the first face
                for i in range(len(image_points)):
                    image_points[i, 0] = faces[0][i][0]
                    image_points[i, 1] = faces[0][i][1]

                for j in range(len(iris_image_points)):
                    iris_image_points[j, 0] = faces[0][j + 468][0]
                    iris_image_points[j, 1] = faces[0][j + 468][1]

                # The third step: pose estimation
                # pose: [[rvec], [tvec]]
                pose = pose_estimator.solve_pose_by_all_points(image_points)

                x_ratio_left, y_ratio_left = FacialFeatures.detect_iris(
                    image_points, iris_image_points, Eyes.LEFT)
                x_ratio_right, y_ratio_right = FacialFeatures.detect_iris(
                    image_points, iris_image_points, Eyes.RIGHT)

                ear_left = FacialFeatures.eye_aspect_ratio(image_points, Eyes.LEFT)
                ear_right = FacialFeatures.eye_aspect_ratio(image_points, Eyes.RIGHT)

                pose_eye = [
                    ear_left, ear_right, x_ratio_left, y_ratio_left, x_ratio_right, y_ratio_right
                ]

                mar = FacialFeatures.mouth_aspect_ratio(image_points)
                mouth_distance = FacialFeatures.mouth_distance(image_points)

                # Stabilize the pose.
                steady_pose = []
                pose_np = np.array(pose).flatten()

                for value, ps_stb in zip(pose_np, pose_stabilizers):
                    ps_stb.update([value])
                    steady_pose.append(ps_stb.state[0])

                steady_pose = np.reshape(steady_pose, (-1, 3))

                # stabilize the eyes value
                steady_pose_eye = []
                for value, ps_stb in zip(pose_eye, eyes_stabilizers):
                    ps_stb.update([value])
                    steady_pose_eye.append(ps_stb.state[0])

                mouth_dist_stabilizer.update([mouth_distance])
                steady_mouth_dist = mouth_dist_stabilizer.state[0]

                # calculate the roll/ pitch/ yaw
                # roll: +ve when the axis pointing upward
                # pitch: +ve when we look upward
                # yaw: +ve when we look left
                roll = np.clip(np.degrees(steady_pose[0][1]), -90, 90)
                pitch = np.clip(-(180 + np.degrees(steady_pose[0][0])), -90, 90)
                yaw = np.clip(np.degrees(steady_pose[0][2]), -90, 90)

                # send info to unity
                if args.connect:
                    # for sending to live2d model (Hiyori)
                    # print('type => ', type(roll), type(mar), type(duration))
                    send_info_to_unity(
                        socket, (roll, pitch, yaw, ear_left, ear_right, x_ratio_left, y_ratio_left,
                                 x_ratio_right, y_ratio_right, mar, mouth_distance, duration))

                if args.debug:
                    print_debug_msg(
                        (roll, pitch, yaw, ear_left, ear_right, x_ratio_left, y_ratio_left,
                         x_ratio_right, y_ratio_right, mar, mouth_distance, duration))

                # pose_estimator.draw_annotation_box(img, pose[0], pose[1], color=(255, 128, 128))

                # pose_estimator.draw_axis(img, pose[0], pose[1])

                pose_estimator.draw_axes(img_facemesh, steady_pose[0], steady_pose[1])

            else:
                # reset our pose estimator
                pose_estimator = PoseEstimator((img_facemesh.shape[0], img_facemesh.shape[1]))

        if args.debug:
            # gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            # cv2.imshow('frame', gray)
            cv2.imshow('Facial landmark', img_facemesh)

        wait_time = int(1000 / cap.get(5))
        print(wait_time)

        key = cv2.waitKey(wait_time)
        
        if key == ord('q') or key == 27:  # Esc
            print('break')
            break
        elif key == 13 or key == 32:  # Enter / Space
            print('play / pause')
            play = play ^ 1
        else:
            if key != -1:
                print(key)

    cap.release()


if __name__ == "__main__":

    parser = ArgumentParser()

    parser.add_argument("-m",
                        "--mode",
                        type=str,
                        help="選擇使用webcam或是輸入影片檔案",
                        choices=["cam", "file"],
                        default=None)

    parser.add_argument("--cam",
                        type=int,
                        help="specify the camera number if you have multiple cameras",
                        default=0)

    parser.add_argument("--connect",
                        action="store_true",
                        help="connect to unity character",
                        default=True)

    parser.add_argument("--debug", action="store_true", help="顯示鏡頭畫面和面部擷取", default=False)

    parser.add_argument(
        "-p",
        "--port",
        type=int,
        help="specify the port of the connection to unity. Have to be the same as in Unity",
        default=5066)

    parser.add_argument("-v",
                        "--file-path",
                        type=str,
                        help="輸入影片所在的位置",
                        default="./lip/base_video/lip_inference.mp4")

    parser.add_argument("--host", type=str, help="設定主機ip或網址", default="0.0.0.0")

    args = parser.parse_args()

    # demo code
    main()
