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
        ydl_opts = {
            'skip_download': True,  # 不下載影片，只下載字幕
            'writesubtitles': False,  # 下載字幕
            'writeautomaticsub': True,  # 下載自動字幕 (如果沒有人工字幕)
            'subtitleslangs': ['en'],  # 選擇字幕語言 (例如 'en'、'zh-TW'、'ja' 等)
            'subtitlesformat': 'vtt',  # 直接下載 VTT 格式
            'outtmpl': os.path.join(CAPTIONS_DIR, '%(id)s.%(ext)s'),  # 儲存位置與檔名
            'quiet': True,
        }

        for yt in data:
            if utils.caption_file_exists(yt):
                print('found existing caption file')
                continue
            else:
                video_id = yt.id
                print(f"正在下載 {video_id} 的字幕...")
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([yt.url])
                self.convert_vtt_to_srt(video_id)
                self.convert_srt_to_txt(video_id)
            except Exception as e:
                print(f"無法下載 {video_id} 的字幕，錯誤: {e}")
        end = time.time()
        print('took', end - start, 'seconds')
        return data

    def convert_vtt_to_srt(self, video_id):
        vtt_path = os.path.join(CAPTIONS_DIR, f"{video_id}.en.vtt")
        srt_path = os.path.join(CAPTIONS_DIR, f"{video_id}.srt")

        if not os.path.exists(vtt_path):
            return

        try:
            webvtt.read(vtt_path).save_as_srt(srt_path)
            print(f"已產生 {video_id}.srt")
            os.remove(vtt_path)
        except Exception as e:
            print(f"轉檔 {video_id} VTT → SRT 失敗，錯誤: {e}")

    def convert_srt_to_txt(self, video_id):
        srt_path = os.path.join(CAPTIONS_DIR, f"{video_id}.srt")
        txt_path = os.path.join(CAPTIONS_DIR, f"{video_id}.txt")

        if not os.path.exists(srt_path):
            print(f"{video_id}下載失敗")
            return

        try:
            # 讀取整個 SRT 檔
            with open(srt_path, 'r', encoding='utf-8') as f:
                srt_content = f.read()
            with open(txt_path, 'w', encoding='utf-8') as txt_file:
                txt_file.write(srt_content)

            print(f"📄 已產生 {video_id}.txt")
            os.remove(srt_path)
        except Exception as e:
            print(f"轉檔 {video_id} SRT → TXT 失敗，錯誤: {e}")
