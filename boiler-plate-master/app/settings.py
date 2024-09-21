from os import environ
from pathlib import Path

BASE_DIR = str(Path(__file__).parent.resolve())
BASE_LOGGER_DIR = Path(__file__).resolve().parent.parent

# Logger configurations
DEFAULT_LOGGER_CONFIG_PATH = BASE_LOGGER_DIR / "logger.ini"

LOGGER_CONFIG_PATH = environ.get(
    "LOGGER_CONFIG_PATH",
    default=DEFAULT_LOGGER_CONFIG_PATH,
)

POSTGRES_HOST = environ.get("POSTGRES_HOST", default="localhost")
POSTGRES_PORT = environ.get("POSTGRES_PORT", default="5432")
POSTGRES_DATABASE = environ.get("POSTGRES_DATABASE", default="boiler_plate")
POSTGRES_USERNAME = environ.get("POSTGRES_USERNAME", default="postgres")
POSTGRES_PASSWORD = environ.get("POSTGRES_PASSWORD", default="postgres")

CONNECTION_CONFIG = {
    "connection_string": f"postgresql+asyncpg://{POSTGRES_USERNAME}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DATABASE}"
}
