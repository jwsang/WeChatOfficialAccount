from pathlib import Path

import yaml
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parents[2]
CONFIG_FILE = BASE_DIR / "config" / "config.yml"
DATA_DIR = BASE_DIR / "data"
STATIC_DIR = BASE_DIR / "app" / "static"
TEMPLATE_DIR = BASE_DIR / "app" / "templates"


def _parse_loose_config_text(text: str) -> dict:
    config: dict = {}
    current_section: dict | None = None

    for raw_line in text.splitlines():
        line = raw_line.rstrip()
        if not line.strip() or line.lstrip().startswith("#"):
            continue

        if not line.startswith(" ") and line.endswith(":"):
            section_name = line[:-1].strip()
            config[section_name] = {}
            current_section = config[section_name]
            continue

        if ":" not in line:
            continue

        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()

        if raw_line.startswith(" ") and current_section is not None:
            current_section[key] = value
        else:
            config[key] = value
            current_section = None

    return config


def load_yaml_config() -> dict:
    if not CONFIG_FILE.exists():
        return {}

    text = CONFIG_FILE.read_text(encoding="utf-8")
    try:
        return yaml.safe_load(text) or {}
    except yaml.YAMLError:
        return _parse_loose_config_text(text)


_yaml_config = load_yaml_config()


class Settings(BaseSettings):
    app_name: str = "工作台"
    app_env: str = "development"
    debug: bool = True
    database_url: str = Field(default=f"sqlite:///{(DATA_DIR / 'app.db').as_posix()}")
    api_key: str = _yaml_config.get("openAi.Key", "") or _yaml_config.get("openAi.Key", "")
    session_secret: str = Field(default="wechat-official-account-dev-secret")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()

DATA_DIR.mkdir(parents=True, exist_ok=True)
STATIC_DIR.mkdir(parents=True, exist_ok=True)
TEMPLATE_DIR.mkdir(parents=True, exist_ok=True)
