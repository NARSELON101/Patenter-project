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


@dataclass
class Config:
    tg_bot: TgBot
    db: DbConfig
    ya_gpt: YaGPT
    debug: bool

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
          api_key=env.str("YAGPT_API_KEY")
        ),
        debug=env.bool("DEBUG", False),
    )
