from argparse import ArgumentParser

from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.video.io.VideoFileClip import VideoFileClip

# import cv2
# def get_video_duration(filename):
#     cap = cv2.VideoCapture(filename)
#     if cap.isOpened():
#         rate = cap.get(5)
#         frame_num = cap.get(7)
#         duration = frame_num / rate
#         return duration
#     return -1


def speedx(clip, factor=None, final_duration=None):
    """
    Returns a clip playing the current clip but at a speed multiplied
    by ``factor``. Instead of factor one can indicate the desired
    ``final_duration`` of the clip, and the factor will be automatically
    computed.
    The same effect is applied to the clip's audio and mask if any.
    """

    if final_duration:
        factor = 1.0 * clip.duration / final_duration
    print(factor)
    newclip = clip.fl_time(lambda t: factor * t, apply_to=['mask', 'audio'])

    if clip.duration is not None:
        newclip = newclip.set_duration(1.0 * clip.duration / factor)

    return newclip


def adjust_duration(audio_file_path, video_input_file_path, video_output_file_path):

    # 時長調整
    video = VideoFileClip(video_input_file_path, audio=False)  # 讀取影片
    # new_video = speedx(video, final_duration=get_video_duration(str(audio_file_path)))
    audio = AudioFileClip(audio_file_path)
    new_video = speedx(video, final_duration=audio.duration)
    audio.close()
    # video.close()
    new_video.write_videofile(video_output_file_path, codec="libx264")
    # , temp_audiofile = "temp-audio.m4a", remove_temp = True , audio_codec="aac"  h264_nvenc libx264


def get_duration(audio_file_path, video_input_file_path):
    video = VideoFileClip(video_input_file_path, audio=False)
    audio = AudioFileClip(audio_file_path)
    video.close()
    audio.close()
    return video.duration,audio.duration


if __name__ == "__main__":
    parser = ArgumentParser()

    parser.add_argument("-a",
                        "--audio-file-path",
                        type=str,
                        help="輸入音檔的檔案位置",
                        default="./lip/base_video/lip_inference.mp4")
    parser.add_argument("-i",
                        "--video-input-file-path",
                        type=str,
                        help="輸入影片的檔案位置",
                        default="./lip/base_video/lip_inference.mp4")
    parser.add_argument("-o",
                        "--video-output-file-path",
                        type=str,
                        help="輸出影片的檔案位置",
                        default="./lip/base_video/lip_inference.mp4")
    args = parser.parse_args()

    adjust_duration(args.audio_file_path, args.video_input_file_path, args.video_output_file_path)
    
    # speed(args.audio_file_path, args.video_input_file_path, args.video_output_file_path)
    # main(
    #     'E:/MyProfile/University/Lab/secondvtn/Virtual-to-News/outputs/7fb09e34-e56c-4c86-880e-2188869e1b5f/lip_inference.mp4',
    #     'E:/MyProfile/University/Lab/secondvtn/Virtual-to-News/outputs/7fb09e34-e56c-4c86-880e-2188869e1b5f/virtual_to_news_temp123.mp4',
    #     'E:/MyProfile/University/Lab/secondvtn/Virtual-to-News/outputs/7fb09e34-e56c-4c86-880e-2188869e1b5f/virtual_to_newsnew.mp4'
    # )