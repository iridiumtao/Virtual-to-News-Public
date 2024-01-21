# TTS使用方法

## 使用demo.py在CLI中運作

```cmd
python demo.py -ge
```

or

```cmd
python demo.py -l -n {filename} -m {rnn or gan} -p {num}
```

### 提供的arg

* -ge: 把samples裡面LJ開頭的檔案當作參考檔案全部試一次
* -l: 讓停頓變長
* -n: {filename}: 傳入參考檔案的名稱
* -m: {rnn or gan}: 選擇rnn或gan作為vocoder
* -p {num}: 提高或降低pitch。正為調高，負為調低

## 使用函式

```python
import argparse
from voice_generator import voiceGenerator
voice = voiceGenerator()
voice.generate(synt_path=None,
                wav_dir=Path() / 'samples',
                wav_name='sample',
                output_dir=Path() / 'assets',
                output_name='voice',
                text='',
                mode='rnn',
                is_long=False,
                shift_pitch=0)
```

### 其中參數

* wav_path: 參考音檔的路徑
* wav_name: 參考音檔的檔名
* output_dir: 輸出的路徑
* output_name: 輸出的檔名
* text: 要生成語音的文字
* mode: 可選擇rnn或gan
* is_long: 是否要讓停頓變長
* shift_pitch: 傳入int調整pitch
