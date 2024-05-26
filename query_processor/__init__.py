from query_processor.processors.letter_maintenance_telegram_query_processor import \
    LetterMaintenanceTelegramQueryProcessor
from query_processor.processors.processing_of_personal_data_telegram_query_processor import \
    PersonalDataTelegramQueryProcessor
from query_processor.processors.user_file_query_processor import UserQueryProcessor
from utils.models import Document

query_processors = [
    LetterMaintenanceTelegramQueryProcessor,
    PersonalDataTelegramQueryProcessor
]


class UserQueryProcessorProxi:

    def __init__(self, file: Document):
        self.file = file

    def __call__(self, use_gpt: bool):
        return UserQueryProcessor(use_gpt, self.file)

    @staticmethod
    def get_name():
        return UserQueryProcessor.get_name()


async def user_query_processor(file_id: int):
    file = await Document.get(file_id)

    return UserQueryProcessorProxi(file)


__all__ = [query_processors]
