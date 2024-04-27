class QueryProcessor:
    __name = None

    @staticmethod
    def get_name():
        pass

    def process_query(self, query: str):
        pass

    async def async_process_query(self, query: str):
        return self.process_query(query)

    def communicate_with_user(self, prompt: str) -> str:
        pass

    async def async_communicate_with_user(self, prompt: str, *args, **kwargs) -> str:
        return self.communicate_with_user(prompt)
