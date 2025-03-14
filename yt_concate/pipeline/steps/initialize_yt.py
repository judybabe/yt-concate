from .step import Step
from yt_concate.model.yt import YT


class InitializeYT(Step):
    def process(self, data, inputs, utils):
        for url in data:
            return [YT(url) for url in data]
