import argparse

from voice_generator import voiceGenerator

voice = voiceGenerator()

def generate_every_samples():
    # 生成每個講者的擬音生成結果
    for i in range(1, 51):
        voice.generate(wav_name=f'LJ{i}.wav', output_fname=f'{i}', text="""歡迎使用工具箱，現已支援中文輸入""")

def open_text():
    # 生成測試用的擬音生成結果
    with open('article.txt', 'r', encoding='utf-8-sig') as f:
        t = f.read()
        return t

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Runs the test for voice generator.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument("-ge", "--generate_every_samples", action="store_true", help="Generate every samples.")
    parser.add_argument("-l","--long", action="store_true", help="Add break.")
    parser.add_argument("-n", "--name", type=str, default="sample", help="The name of the input file.")
    parser.add_argument("-m", "--mode", type=str, default="rnn", help="The mode of the test.")
    parser.add_argument("-p", "--pitch", type=int, default=0, help="The pitch of the test.")
    args = parser.parse_args()

    if args.generate_every_samples:
        generate_every_samples()
    else:
        voice.generate(wav_name=args.name, mode=args.mode, is_long=args.long, shift_pitch=args.pitch, text=open_text())