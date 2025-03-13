import os
import yt_dlp
import webvtt

from .step import Step
from .step import StepException
from yt_concate.settings import CAPTIONS_DIR

import time


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

        for url in data:
            if utils.caption_file_exists(url):
                print('found existing caption file')
                continue
            else:
                video_id = utils.get_video_id_from_url(url)
                print(f"正在下載 {video_id} 的字幕...")
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])
                self.convert_vtt_to_srt(video_id)
                self.convert_srt_to_txt(video_id)
            except Exception as e:
                print(f"無法下載 {video_id} 的字幕，錯誤: {e}")
        end = time.time()
        print('took', end - start, 'seconds')

    def convert_vtt_to_srt(self, video_id):
        """
        使用 webvtt 將 <video_id>.en.vtt 轉成 <video_id>.srt
        """
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
        """
        讀取 <video_id>.srt，過濾掉編號與時間軸，最後存成 <video_id>.txt
        """
        srt_path = os.path.join(CAPTIONS_DIR, f"{video_id}.srt")
        txt_path = os.path.join(CAPTIONS_DIR, f"{video_id}.txt")

        if not os.path.exists(srt_path):
            print(f"{video_id}下載失敗")
            return

        try:
            # 讀取整個 SRT 檔
            with open(srt_path, 'r', encoding='utf-8') as f:
                srt_content = f.read()

            # 不做任何過濾，直接寫入 .txt
            with open(txt_path, 'w', encoding='utf-8') as txt_file:
                txt_file.write(srt_content)

            print(f"📄 已產生 {video_id}.txt，並保留 SRT 格式行。")
            os.remove(srt_path)

        except Exception as e:
            print(f"轉檔 {video_id} SRT → TXT 失敗，錯誤: {e}")
