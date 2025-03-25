
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
                'skip_download': True,
                'writesubtitles': True,
                'writeautomaticsub': True,
                'subtitleslangs': ['zh'],
                'outtmpl': os.path.join(CAPTIONS_DIR, '%(id)s'),
                'nooverwrites': True,
            }

            try:
                video_id = yt.id
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([yt.url])
                self.vtt_to_srt(video_id)
                self.convert_srt_to_txt(video_id)
            except Exception as e:
                print(f"無法下載 {video_id} 的字幕，錯誤: {e}")
                continue

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
            with open(srt_path, 'r', encoding="utf-8") as f:
                srt_content = f.read()
            with open(txt_path, 'w', encoding="utf-8") as txt_file:
                txt_file.write(srt_content)

            print(f"📄 已產生 {video_id}.txt")
            os.remove(srt_path)
        except Exception as e:
            print(f"轉檔 {video_id} SRT → TXT 失敗，錯誤: {e}")
    def vtt_to_srt(self, video_id):
        vtt_path = os.path.join(CAPTIONS_DIR, f"{video_id}.zh.vtt")
        srt_path = os.path.join(CAPTIONS_DIR, f"{video_id}.srt")
        captions = webvtt.read(vtt_path)
        captions.save_as_srt(srt_path)
        os.remove(vtt_path)
    def fix_youtube_vtt(self, video_id):
        pretty_subtitle = ''
        previous_caption_text = ''
        vtt_path = os.path.join(CAPTIONS_DIR, f"{video_id}.zh.vtt")
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
