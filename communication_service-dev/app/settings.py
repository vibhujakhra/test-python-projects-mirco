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
POSTGRES_DATABASE = environ.get("POSTGRES_DATABASE", default="communication")
POSTGRES_USERNAME = environ.get("POSTGRES_USERNAME", default="postgres")
POSTGRES_PASSWORD = environ.get("POSTGRES_PASSWORD", default="postgres")
db_url = f"postgresql+asyncpg://{POSTGRES_USERNAME}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DATABASE}"

EMAIL_CONFIGURATION = {
    "username": environ.get("MAIL_USERNAME", default="AKIA5RUCV4Q43CKBSMUK"),
    "password": environ.get("MAIL_PASSWORD", default="BDyqlfdp4hM168AkBW+5xJcNz/EDW/yf4Oq7yXWIBs4X"),
    "from": environ.get("MAIL_FROM", default="support@renwewbuy.in"),
    "port": environ.get("MAIL_PORT", default=587),
    "server": environ.get("MAIL_SERVER", default="email-smtp.ap-south-1.amazonaws.com"),
    "title": environ.get("MAIL_TITLE", default="RenewBuy Email"),
    "mail_tls": environ.get("MAIL_TLS", default=True),
    "mail_ssl": environ.get("MAIL_SSL", default=False),
    "use_credentials": environ.get("USE_CREDENTIALS", default=True)
}
KAFKA = {
    "bootstrap_servers": environ.get("KAFKA_BROKER", default="localhost:9092"),
    "topic": {
        "email_topic": environ.get('KAFKA_EMAIL_TOPIC', default='email_topic'),
        "otp_topic": environ.get('KAFKA_OTP_TOPIC', default='otp_topic'),
        "sms_topic": environ.get("KAFKA_SMS_TOPIC", default="sms_topic"),
    }
}

CONNECTION_CONFIG = {
    "connection_string": f"postgresql+asyncpg://{POSTGRES_USERNAME}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DATABASE}"
}

KALEYRA_SENDER_ID = environ.get("KALEYRA_SENDER_ID", default="RNWBUY")
KALEYRA_API_KEY = environ.get("KALEYRA_API_KEY", default="A40a56476403b8a1cc066694f0ac6bfac")
KALEYRA_URL = environ.get("KALEYRA_URL",
                          default="https://api-alerts.kaleyra.com/v4/?api_key={KALEYRA_API_KEY}&method=sms&message={message}&to={mobile_no}&sender={KALEYRA_SENDER_ID}&template_id={dlt_template_id}")
PROXY_URL = environ.get("PROXY_URL", default="")
