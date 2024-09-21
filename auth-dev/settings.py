from pathlib import Path
from os import environ
from dotenv import load_dotenv

load_dotenv(override=True)

BASE_DIR = Path(__file__).resolve().parent.parent

# Logger configurations
DEFAULT_LOGGER_CONFIG_PATH = BASE_DIR / "logger.ini"

LOGGER_CONFIG_PATH = environ.get(
    "LOGGER_CONFIG_PATH",
    default=DEFAULT_LOGGER_CONFIG_PATH,
)

JWT_TOKEN_TIME = int(environ.get("JWT_TOKEN_TIME", 12 * 60 * 60))
RESET_PASSWORD_JWT_TOKEN_TIME = int(environ.get("JWT_TOKEN_TIME", 15 * 60))
JWT_TOKEN_SECRET = environ.get("JWT_TOKEN_SECRET", "nrQADaPqS65s8Ejc")
JWT_ALGORITHM = environ.get("JWT_ALGORITHM", "HS256")
RESET_PASSWORD_KEY = environ.get("JWT_RESET_PASSWORD_KEY", "2szbGDkDr7MoK")
ERROR_FILE_URL = environ.get("ERROR_FILE_URL",
                             default="http://dataverse.sleepdev.renewbuy.in/api/v1/download_error_report?file_name={}")
AUTO_LOGOUT_TIMER = environ.get("AUTO_LOGOUT_TIMER", 30 * 60)


POSTGRES_HOST = environ.get("POSTGRES_HOST", default="127.0.0.1")
POSTGRES_PORT = environ.get("POSTGRES_PORT", default="5432")
POSTGRES_DATABASE = environ.get("POSTGRES_DATABASE", default="boiler_plate")
POSTGRES_USERNAME = environ.get("POSTGRES_USERNAME", default="renewbuy")
POSTGRES_PASSWORD = environ.get("POSTGRES_PASSWORD", default="Renew2022")

CONNECTION_CONFIG = {
    "connection_string":  f"postgresql+asyncpg://{POSTGRES_USERNAME}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DATABASE}" }
KAFKA = {
    "bootstrap_servers": environ.get("KAFKA_BROKER", default="localhost:9092"),
    "topic": {
        "email_topic": environ.get("KAFKA_EMAIL_TOPIC", default="EMAIL"),
        "mobile_topic": environ.get("KAFKA_MOBILE_TOPIC", default="MOBILE"),
   }
}
DOMAIN_ADDRESS = environ.get("DOMAIN_ADDRESS_AUTH", default="http://auth.sleepdev.renewbuy.in")
VERIFICATION_EMAIL_SUBJECT = environ.get("VERIFICATION_EMAIL_SUBJECT", default="RenewBuy Confirmation Email")
RESET_DOMAIN_ADDRESS = environ.get("RESET_DOMAIN_ADDRESS", default="http://misp-signup.sleepdev.renewbuy.in")



ams_creds = {
    'Content-Type': 'application/json',
    'API-KEY': environ.get('AMS_API_KEY', '945dbc41-8587-4c62-82ca-741f914077cf'),
    'SECRET-KEY': environ.get('AMS_SECRET_KEY', 'dCr8hEr8WWaSlxoNrh6Dst9PLzWQJnqD'),
    'X-API-Key': environ.get('AMS_X_API_KEY', 'MpVo4Z9z4bffDpRtqxvQWDqKdWy5Q735')
}

SERVICE_CREDENTIALS = {
    "ams_service": {
        "dns": environ.get("AMS_URI", default="https://accounts.rbstaging.in"),
        "headers": {}
    }
}

PROXY_URL = environ.get('PROXY_URL', default='')
