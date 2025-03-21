from .step import Step
from moviepy import VideoFileClip, concatenate_videoclips


class EditVideos(Step):
    def process(self, data, inputs, utils):
        clips = []
        for found in data:
            print(found.time)
            start, end = self.parse_caption_time(found.time)
            print(start, end)
            video = VideoFileClip(found.yt.video_filepath).subclipped(start, end)
            clips.append(video)
            if len(clips) >= inputs['limit']:
                break

        final_clip = concatenate_videoclips(clips)
        output_filepath = utils.get_output_filepath(inputs['channel_id'], inputs['search_word'])
        final_clip.write_videofile(output_filepath)

    def parse_caption_time(self, caption_time):
        start, end = caption_time.split(' --> ')
        return self.parse_time_str(start), self.parse_time_str(end)

    def parse_time_str(self, time_str):
        h, m, s = time_str.split(':')
        s, ms = s.split(',')
        total = int(h), int(m), int(s) + int(ms) / 1000
        return total
