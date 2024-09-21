from os import environ
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Logger configurations
DEFAULT_LOGGER_CONFIG_PATH = BASE_DIR / "logger.ini"

LOGGER_CONFIG_PATH = environ.get(
    "LOGGER_CONFIG_PATH",
    default=DEFAULT_LOGGER_CONFIG_PATH,
)

POSTGRES_HOST = environ.get("POSTGRES_HOST", default="13.233.140.161")
POSTGRES_PORT = environ.get("POSTGRES_PORT", default="5432")
POSTGRES_DATABASE = environ.get("POSTGRES_DATABASE", default="pricing_db")
POSTGRES_USERNAME = environ.get("POSTGRES_USERNAME", default="price_user")
POSTGRES_PASSWORD = environ.get("POSTGRES_PASSWORD", default="price_password")

db_url = f"postgresql+asyncpg://{POSTGRES_USERNAME}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DATABASE}"

AUTH_LOGIN_URL = environ.get("AUTH_LOGIN_URL", default="http://auth.sleepdev.renewbuy.in/auth/jwt/login")

SERVICE_CREDENTIALS = {
    "dataverse": {
        "dns": environ.get("DATAVERSE_DNS", default="http://dataverse.sleepdev.renewbuy.in"),
        "headers": {}
    }
}

CONNECTION_CONFIG = {
    "connection_string": f"postgresql+asyncpg://{POSTGRES_USERNAME}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DATABASE}"
}