from query_processor.processors.letter_maintenance_telegram_query_processor import LetterMaintenanceTelegramQueryProcessor
from query_processor.processors.processing_of_personal_data_query_processor import PersonalDataQueryProcessor

query_processors = [
    LetterMaintenanceTelegramQueryProcessor,
    PersonalDataQueryProcessor
]

__all__ = [query_processors]