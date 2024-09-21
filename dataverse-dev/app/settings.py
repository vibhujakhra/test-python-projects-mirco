from os import environ
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(override=True)
# Logger configurations
DEFAULT_LOGGER_CONFIG_PATH = BASE_DIR / "logger.ini"

LOGGER_CONFIG_PATH = environ.get(
    "LOGGER_CONFIG_PATH",
    default=DEFAULT_LOGGER_CONFIG_PATH,
)

POSTGRES_HOST = environ.get("POSTGRES_HOST", default="localhost")
POSTGRES_PORT = environ.get("POSTGRES_PORT", default="5432")
POSTGRES_DATABASE = environ.get("POSTGRES_DATABASE", default="dataverse")
POSTGRES_USERNAME = environ.get("POSTGRES_USERNAME", default="postgres")
POSTGRES_PASSWORD = environ.get("POSTGRES_PASSWORD", default="renewbuY#123")

AUTH_LOGIN_URL = environ.get("AUTH_LOGIN_URL", default="http://auth.sleepdev.renewbuy.in/auth/jwt/login")
AUTH_REGISTER_URL = environ.get("AUTH_REGISTER_URL", default="http://auth.sleepdev.renewbuy.in/auth/register")

ERROR_FILE_URL = environ.get("ERROR_FILE_URL",
                             default="http://dataverse.sleepdev.renewbuy.in/api/v1/download_error_report?file_name={}")
CONNECTION_CONFIG = {
    "connection_string": f"postgresql+asyncpg://{POSTGRES_USERNAME}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DATABASE}"
}
S3_BUCKET_URL = environ.get("S3_BUCKET_URL", default="sleep-dev.s3.ap-south-1.amazonaws.com")
# PAYMENT_MODE_URL = environ.get("PAYMENT_MODE_URL", default="http://muneem.sleepdev.renewbuy.in/api/v1/payment_mode/")

SERVICE_CREDENTIALS = {
    "muneem": {
        "dns": environ.get("MUNEEM_URI", default="http://muneem.sleepdev.renewbuy.in"),
        "headers": {'Content-Type': 'application/json'}
    }
}
USER_PASSWORD = environ.get("USER_PASSWORD", default="pass@123")
AUTH_REGISTER_URL = environ.get("AUTH_REGISTER_URL", default="http://auth.sleepdev.renewbuy.in/auth/register")
PAYMENT_LIST_URL = environ.get("PAYMENT_LIST_URL", default="http://muneem.sleepdev.renewbuy.in/api/v1/payment_mode/")
USER_DETAILS_URL = environ.get("USER_DETAILS_URL", default="http://auth.sleepdev.renewbuy.in/api/v1/get_user_details/")
USER_DETAILS_UPDATE_URL = environ.get("USER_DETAILS_UPDATE_URL", default="http://auth.sleepdev.renewbuy.in/api/v1"
                                                                         "/edit_user_detail/")
