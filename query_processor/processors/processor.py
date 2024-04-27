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

    async def async_communicate_with_user(self, prompt: str, *args, **kwargs):
        if hasattr(self, 'tg_dispatcher'):
            bot = self.tg_dispatcher.bot
            dispatcher = self.tg_dispatcher
            state = self.tg_dispatcher.current_state()
        else:
            raise AttributeError("tg_dispatcher не найден")
        if args is not None:
            sep = ' '
            if kwargs is not None:
                sep = kwargs.get('sep', ' ')
            for arg in args:
                prompt += sep
                prompt += str(arg)
        return await dispatcher.bot.send_message(state.chat, prompt)
