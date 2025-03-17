import os
import time
import yt_dlp
import webvtt


from .step import Step
from .step import StepException
from yt_concate.settings import CAPTIONS_DIR


class DownloadCaptions(Step):

    def process(self, data, inputs, utils):
        start = time.time()
        for yt in data:
            if utils.caption_file_exists(yt):
                print('found existing caption file')
                continue

            ydl_opts = {
                'skip_download': True,  # 不下載影片，只下載字幕
                'writeautomaticsub': True,
                'subtitleslangs': ['en'],  # 選擇字幕語言 (例如 'en'、'zh-TW'、'ja' 等)
                'outtmpl': os.path.join(CAPTIONS_DIR, '%(id)s.%(ext)s'),  # 儲存位置與檔名
                'nooverwrites': True,
            }

            try:
                video_id = yt.id
                print(f"正在下載 {video_id} 的字幕...")
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([yt.url])
                self.fix_youtube_vtt(video_id)
                self.convert_srt_to_txt(video_id)
            except Exception as e:
                print(f"無法下載 {video_id} 的字幕，錯誤: {e}")
        end = time.time()
        print('took', end - start, 'seconds')

        return data
    def convert_srt_to_txt(self, video_id):
        srt_path = os.path.join(CAPTIONS_DIR, f"{video_id}.srt")
        txt_path = os.path.join(CAPTIONS_DIR, f"{video_id}.txt")

        if not os.path.exists(srt_path):
            print(f"{video_id}下載失敗")
            return

        try:
            # 讀取整個 SRT 檔
            with open(srt_path, 'r') as f:
                srt_content = f.read()
            with open(txt_path, 'w') as txt_file:
                txt_file.write(srt_content)

            print(f"📄 已產生 {video_id}.txt")
            os.remove(srt_path)
        except Exception as e:
            print(f"轉檔 {video_id} SRT → TXT 失敗，錯誤: {e}")

    def fix_youtube_vtt(self, video_id):
        pretty_subtitle = ''
        previous_caption_text = ''
        vtt_path = os.path.join(CAPTIONS_DIR, f"{video_id}.en.vtt")
        srt_path = os.path.join(CAPTIONS_DIR, f"{video_id}.srt")
        i = 1
        for caption in webvtt.read(vtt_path):

            if previous_caption_text == caption.text.strip():

                converted_start = previous_caption_start.replace('.', ',')
                converted_end = caption.end.strip().replace('.', ',')

                pretty_subtitle += f"{i}\n{converted_start} --> {converted_end}\n{previous_caption_text}\n\n"

                i += 1

            elif previous_caption_text == caption.text.strip().split("\n")[0]:

                previous_caption_text = caption.text.strip().split("\n")[1]
                previous_caption_start = caption.start
                last_caption_end = caption.end

            else:
                previous_caption_text = caption.text.strip()
                previous_caption_start = caption.start.strip()

        with open(srt_path, 'w') as srt_file:
            srt_file.write(pretty_subtitle)
        os.remove(vtt_path)
