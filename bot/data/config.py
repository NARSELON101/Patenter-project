from dataclasses import dataclass

from environs import Env

@dataclass
class DbConfig:
    postgres_uri: str

@dataclass
class TgBot:
    token: str

@dataclass
class Config:
    tg_bot: TgBot
    db: DbConfig

def load_config(path: str = None):
    env = Env()
    env.read_env(path)

    return Config(
        tg_bot=TgBot(
            token=env.str("BOT_TOKEN")
        ),
        db=DbConfig(
            postgres_uri=env.str("POSTGRES_URI")
        )
    )