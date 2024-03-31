from query_processor.data_source.source import DataSource


class ConsoleDataSource(DataSource):
    def __init__(self, prompt):
        self.prompt = prompt

    def get(self, *args, **kwargs):
        return input(self.prompt)
