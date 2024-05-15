import pathlib
from dataclasses import dataclass

from environs import Env


@dataclass
class DbConfig:
    postgres_uri: str


@dataclass
class TgBot:
    token: str


@dataclass
class YaGPT:
    catalog_id: str
    api_key: str
    time_to_sleep: float


@dataclass
class UserFileStorage:
    path: pathlib.Path


@dataclass
class Config:
    tg_bot: TgBot
    db: DbConfig
    ya_gpt: YaGPT
    debug: bool
    user_file_storage: UserFileStorage

    def __getitem__(self, item: str):
        if hasattr(self, item):
            return getattr(self, item)
        return None

    def get(self, item, or_else=None):
        return self[item] or or_else


def load_config(path: str = None):
    env = Env()
    env.read_env(path)

    return Config(
        tg_bot=TgBot(
            token=env.str("BOT_TOKEN")
        ),
        db=DbConfig(
            postgres_uri=env.str("POSTGRES_URI")
        ),
        ya_gpt=YaGPT(
            catalog_id=env.str("YAGPT_CATALOG_ID"),
            api_key=env.str("YAGPT_API_KEY"),
            time_to_sleep=env.float("YAGPT_TIME_TO_SLEEP")
        ),
        debug=env.bool("DEBUG", False),
        user_file_storage=UserFileStorage(
            path=pathlib.Path(env.str("USER_DOCUMENTS_STORE"))
        )
    )
