from os import environ
from pathlib import Path
import logging

from dotenv import load_dotenv

load_dotenv()
BASE_DIR = Path(__file__).resolve().parent.parent

# Logger configurations
DEFAULT_LOGGER_CONFIG_PATH = BASE_DIR / "logger.ini"

LOGGER_CONFIG_PATH = environ.get(
    "LOGGER_CONFIG_PATH",
    default=DEFAULT_LOGGER_CONFIG_PATH,
)

logging.config.fileConfig(DEFAULT_LOGGER_CONFIG_PATH)

POSTGRES_HOST = environ.get("POSTGRES_HOST", default="localhost")
POSTGRES_PORT = environ.get("POSTGRES_PORT", default="5432")
POSTGRES_DATABASE = environ.get("POSTGRES_DATABASE", default="documentic")
POSTGRES_USERNAME = environ.get("POSTGRES_USERNAME", default="postgres")
POSTGRES_PASSWORD = environ.get("POSTGRES_PASSWORD", default="postgres")
db_url = f"postgresql+asyncpg://{POSTGRES_USERNAME}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DATABASE}"
S3_ASSET_URL = environ.get("S3_ASSET_URL",default="sleep-dev.s3.ap-south-1.amazonaws.com")
CONNECTION_CONFIG = {
    "connection_string": f"postgresql+asyncpg://{POSTGRES_USERNAME}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DATABASE}"
}

KAFKA = {
    "bootstrap_servers": environ.get("KAFKA_BROKER", default="localhost:9092"),
    "topic_name": environ.get("KAFKA_TOPIC", default='policy_generation_data')
}

motor_policy_download_url = environ.get("MOTOR_POLICY_DOWNLOAD_URL",
                                        default="http://localhost:8000/api/v1/motor/download/policy/{}")

AUTH_LOGIN_URL = environ.get("AUTH_LOGIN_URL", default="http://auth.sleepdev.renewbuy.in/auth/jwt/login")
DOCUMENT_DNS_CONFIG = environ.get("DOCUMENT_DNS_CONFIG", default="http://cabinet.sleepdev.renewbuy.in")

SERVICE_CREDENTIALS = {
    "dataverse": {
        "dns": environ.get("DATAVERSE_URI", default="http://dataverse.sleepdev.renewbuy.in"),
        "headers": {'Content-Type': 'application/json'}
    },
    "cleverbridge": {
        "dns": environ.get("CLEVERBRIDGE_URI", default="http://cleverbridge.sleepdev.renewbuy.in"),
        "headers": {'Content-Type': 'application/json'}
    },
    "policy": {
        "dns": environ.get("WINTERFELL_URI", default="http://winterfell.sleepdev.renewbuy.in"),
        "headers": {'Content-Type': 'application/json'}
    },
    "auth": {
        "dns": environ.get("AUTH_URI", default="http://auth.sleepdev.renewbuy.in"),
        "headers": {'Content-Type': 'application/json'}
    },
    "quotes": {
        "dns": environ.get("QUAKE_DNS", default="http://quotes.sleepdev.renewbuy.in"),
        "headers": {}
    }
}
