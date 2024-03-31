from datetime import datetime

from query_processor.data_source.source import DataSource


class DateNowDataSource(DataSource):
    def __init__(self, fmt: str = '%d %B %Y'):
        self.fmt = fmt

    def get(self, *args, **kwargs):
        return datetime.now().strftime(self.fmt)
