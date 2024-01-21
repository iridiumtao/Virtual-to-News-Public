import io
import re
from pathlib import Path

import cn2an
import librosa
import numpy as np
import soundfile as sf
from encoder import inference as encoder
from scipy.io.wavfile import write
from synthesizer.inference import Synthesizer
from vocoder.hifigan import inference as gan_vocoder
from vocoder.wavernn import inference as rnn_vocoder


class voiceGenerator:

    def __init__(self):
        self.syn_models_dirt = Path() / 'synthesizer' / 'saved_models'
        self.synthesizers = list(Path(self.syn_models_dirt).glob('**/*.pt'))
        self.synthesizers_cache = {}
        encoder.load_model(Path() / 'encoder' / 'saved_models' / 'pretrained.pt')
        rnn_vocoder.load_model(Path() / "vocoder" / "saved_models" / "pretrained" / "pretrained.pt")
        gan_vocoder.load_model(Path() / 'vocoder' / 'saved_models' / 'pretrained' / 'g_hifigan.pt')

    def generate(self,
                 synt_path=None,
                 wav_dir=Path() / 'samples',
                 wav_name='sample',
                 output_dir=Path() / 'assets',
                 output_name='voice',
                 text='',
                 mode='rnn',
                 is_long=False,
                 shift_pitch=0):
        # 如果路徑不存在就創資料夾
        wav_dir.mkdir(parents=True, exist_ok=True)
        output_dir.mkdir(parents=True, exist_ok=True)

        # Load synthesizer
        if synt_path is None:
            synt_path = self.synthesizers[0]
            print("NO synthsizer is specified, try default first one.")
        if self.synthesizers_cache.get(synt_path) is None:
            current_synt = Synthesizer(Path(synt_path))
            self.synthesizers_cache[synt_path] = current_synt
        else:
            current_synt = self.synthesizers_cache[synt_path]
        print("using synthesizer model: " + str(synt_path))
        # Load input wav
        # wav, sample_rate, = librosa.load(wav_path)
        wav = wav = Synthesizer.load_preprocess_wav(f'{wav_dir}/{wav_name}.wav')
        # Make sure we get the correct wav
        temp_wav_path = Path() / 'assets'
        temp_wav_path.mkdir(exist_ok=True, parents=True)
        write(Path() / 'assets' / 'temp.wav', Synthesizer.sample_rate, wav)
        encoder_wav = encoder.preprocess_wav(wav, Synthesizer.sample_rate)
        embed, _, _ = encoder.embed_utterance(encoder_wav, return_partials=True)

        # Load input text
        texts = text.split("\n")
        punctuation = '！，。、,'  # punctuate and split/clean text
        lonely_num = ''
        processed_texts = []
        for text in texts:
            for processed_text in re.sub(r'[{}]+'.format(punctuation), '\n', text).split('\n'):
                if processed_text:
                    # 處理如果單一數字前後都是逗號會被斷爛的情況
                    if processed_text.isdecimal():
                        lonely_num = processed_text
                        continue
                    if lonely_num != '':
                        processed_text = processed_texts.pop() + lonely_num + processed_text
                        lonely_num = ''
                    # 處理有括號的情況
                    processed_text = re.sub('（.*?）|\(.*?\)', '', processed_text)
                    if processed_text == '':
                        continue
                    # 處理數字轉換
                    processed_text = cn2an.transform(processed_text, 'an2cn')
                    processed_texts.append(processed_text.strip())
        texts = processed_texts

        # synthesize and vocode
        embeds = [embed] * len(texts)
        specs = current_synt.synthesize_spectrograms(texts, embeds)
        breaks = [spec.shape[1] for spec in specs]
        spec = np.concatenate(specs, axis=1)
        if mode == 'rnn':
            wav = rnn_vocoder.infer_waveform(spec)
        elif mode == 'gan':
            wav = gan_vocoder.infer_waveform(spec)
        else:
            raise ValueError("mode should be rnn or gan")

        # Add breaks
        if is_long:
            b_ends = np.cumsum(np.array(breaks) * Synthesizer.hparams.hop_size)
            b_starts = np.concatenate(([0], b_ends[:-1]))
            wavs = [wav[start:end] for start, end, in zip(b_starts, b_ends)]
            breaks = [np.zeros(int(0.15 * Synthesizer.sample_rate))] * len(breaks)
            wav = np.concatenate([i for w, b in zip(wavs, breaks) for i in (w, b)])

        # shift pitch
        if shift_pitch != 0:
            wav = librosa.effects.pitch_shift(wav, Synthesizer.sample_rate, n_steps=shift_pitch)

        # Return cooked wav
        wav = wav / np.abs(wav).max() * 0.97
        out = io.BytesIO()
        write(out, Synthesizer.sample_rate, wav)
        sf.write(f'{output_dir}/{output_name}.wav', wav, Synthesizer.sample_rate)
