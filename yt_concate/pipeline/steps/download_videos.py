import os.path
import yt_dlp
from yt_concate.settings import VIDEOS_DIR

from .step import Step


class DownloadVideos(Step):

    def process(self, data, inputs, utils):
        print(len(data))
        yt_set = set([found.yt for found in data])
        print('videos to download=', len(yt_set))

        ydl_opts = {
            'outtmpl': os.path.join(VIDEOS_DIR, '%(id)s.%(ext)s'),
            'format': 'bestvideo[vcodec=h264][height<=480]+bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegVideoConvertor',
                'preferedformat': 'mp4'
            }],
            'download_archive': 'archive.txt'
        }

        for yt in yt_set:
            url = yt.url
            if utils.video_file_exists(yt):
                print(f'found existing video file for {url}, skipping..')
                continue

            print('downloading', url)
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

        return data
