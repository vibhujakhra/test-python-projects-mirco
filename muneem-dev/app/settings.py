from os import environ
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(override=True)
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
POSTGRES_DATABASE = environ.get("POSTGRES_DATABASE", default="muneem")
POSTGRES_USERNAME = environ.get("POSTGRES_USERNAME", default="postgres")
POSTGRES_PASSWORD = environ.get("POSTGRES_PASSWORD", default="postgres")

KAFKA = {
    "bootstrap_servers": environ.get("KAFKA_BROKER", default="localhost:9092"),
    "topic": {
        "email_topic": environ.get('KAFKA_EMAIL_TOPIC', default='EMAIL'),
        "otp_topic": environ.get('KAFKA_OTP_TOPIC', default='otp_topic'),
    }
}

DOMAIN_ADDRESS = environ.get("DOMAIN_ADDRESS_MUNEEM", default="http://muneem.sleepdev.renewbuy.in")
DOMAIN_ADDRESS_SERVER = environ.get("DOMAIN_ADDRESS_SERVER", default="http://misp.sleepdev.renewbuy.in")
VERIFICATION_EMAIL_SUBJECT = environ.get("VERIFICATION_EMAIL_SUBJECT", default="RenewBuy Consent Confirmation Email")
DATAVERSE_DNS = environ.get('DATAVERSE_DNS')
download_url = environ.get('DOWNLOAD_URL', default='http://cabinet.sleepdev.renewbuy.in/get_document/')
bucket_name = environ.get('BUCKET_NAME', default='sleep-dev')

AUTH_LOGIN_URL = environ.get("AUTH_LOGIN_URL", default="http://auth.sleepdev.renewbuy.in/auth/jwt/login")

SERVICE_CREDENTIALS = {
    "dataverse": {
        "dns": environ.get("DATAVERSE_DNS", default="http://dataverse.sleepdev.renewbuy.in"),
        "headers": {}
    },
    "cleverbridge": {
        "dns": environ.get("CLEVERBRIDGE_DNS", default="http://cleverbridge.sleepdev.renewbuy.in"),
        "headers": {"accept": "application/json"}
    },
    "policy": {
        "dns": environ.get("WINTERFELL_DNS", default="http://winterfell.sleepdev.renewbuy.in"),
        "headers": {}
    },
    "proposal": {
        "dns": environ.get("TURTLES_DNS", default="http://turtles.sleepdev.renewbuy.in"),
        "headers": {}
    },
    "auth": {
        "dns": environ.get("AUTH_URI", default="http://auth.sleepdev.renewbuy.in"),
        "headers": {}
    },
    "callback": {
        "dns": environ.get("CALLBACK_DNS", default="http://paymentlayer.sleepdev.renewbuy.in"),
        "headers": {}
    },
    "rb_coordinator": {
        "dns": environ.get("INGESTION_URI", default="http://rb_coordinator.sleepdev.renewbuy.in"),
        "headers": {'Content-Type': 'application/json'}
    }
}

CONNECTION_CONFIG = {
    "connection_string": f"postgresql+asyncpg://{POSTGRES_USERNAME}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DATABASE}"
}

OTP_EXPIRY_SEC = environ.get("OTP_EXPIRY", default=60)
GATEWAY_ENCRYPTION_KEY = environ.get('GATEWAY_ENCRYPTION_KEY', default='xZUALTOyX6xlMm7p1nqCjlxcrBZckjB1nvDf6sIATwk=')

INSURER_SETTINGS = {
    "rgi": {
        "reliance_proposal_api_url": environ.get('reliance_proposal_api_url',
                                                 default='http://rgiclservices.reliancegeneral.co.in/Xpas_Motor_OEM_API/api/GeneratePolicyNumber/RenewBuyPolicyNumber'),
        "reliance_payment_api_url": environ.get('reliance_payment_api_url',
                                                default='http://rgiclservices.reliancegeneral.co.in/Xpas_Motor_OEM_API/api/GeneratePolicyNumber/RenewBuyPolicyPayment'),
        "reliance_ckyc_api_url": environ.get("reliance_ckyc_api_url",
                                             default="https://api.brobotinsurance.com/binary_ckyc/CKYCApi/api/CKYCService/Verify_CKYC"),
        "reliance_ckyc_status_api_url": environ.get("reliance_ckyc_status_api_url",
                                                    default="https://api.brobotinsurance.com/Verify_CKYC_Details"),
        "policy_summary_api_url": environ.get('policy_summary_api_url',
                                              default="http://dataverse.sleepdev.renewbuy.in/api/v1/policy_summary/?"),
        "fetch_ckyc_subscription_key": environ.get('reliance_fetch_ckyc_subscription_key',
                                                   default='8874866a8aaf462385ef3f3b8c4efe34'),
        "fetch_ckyc_content_type": environ.get('reliance_fetch_ckyc_content_type', default='application/json'),
        "customer_ckyc_data_url": environ.get('customer_ckyc_data_url',
                                              default="http://customerservice.sleepdev.renewbuy.in/v1/ckyc/get_customer_ckyc_data/")
    },

    "usgi": {
        "universal_sompo_auth_api_url": environ.get('universal_sompo_auth_api_url',
                                                    default='https://uat.universalsompo.in/AmpereEV_Integration/api/EV2W/getToken'),
        "universal_sompo_auth_api_username": environ.get('universal_sompo_auth_api_username', default='usgi_renewbuy'),
        "universal_sompo_auth_api_passward": environ.get('universal_sompo_auth_api_passward',
                                                         default='usgi_renewbuy!@2023'),
        "universal_sompo_proposal_api_url": environ.get('universal_sompo_proposal_api_url',
                                                        default='https://uat.universalsompo.in/AmpereEV_Integration/api/EV2W/ProposalService'),
        "policy_summary_api_url": environ.get('policy_summary_api_url',
                                              default="http://dataverse.sleepdev.renewbuy.in/api/v1/policy_summary/?"),
        "customer_ckyc_data_url": environ.get('customer_ckyc_data_url',
                                              default="http://customerservice.sleepdev.renewbuy.in/v1/ckyc/get_customer_ckyc_data/"),
        "universal_sompo_payment_api_url": environ.get('universal_sompo_payment_api_url',
                                                       default='https://uat.universalsompo.in/AmpereEV_Integration//api/EV2W/PaymentService'),
        "universal_sompo_ckyc_api_url": environ.get('universal_sompo_ckyc_api_url',
                                                    default='https://uat.universalsompo.in/CKYC_API/api/Ampere/CKYC/searchDownload'),
        "universal_sompo_ckyc_status_api_url": environ.get('universal_sompo_ckyc_status_api_url',
                                                           default='https://uat.universalsompo.in/CKYC_API/api/Ampere/CKYC/enquiry'),
    },

    "hcg": {
        "hdfc_ergo_auth_api_url": environ.get('hdfc_ergo_auth_api_url',
                                              default='https://ekyc-uat.hdfcergo.com/e-kyc/tgt/generate-token'),
        "hdfc_ergo_proposal_api_url": environ.get('hdfc_ergo_proposal_api_url',
                                                  default='https://accessuat.hdfcergo.com/oem/INTEGRATION/API/Ampere/GeneratePolicy'),
        "policy_summary_api_url": environ.get('policy_summary_api_url',
                                              default="http://dataverse.sleepdev.renewbuy.in/api/v1/policy_summary/?"),
        "customer_ckyc_data_url": environ.get('customer_ckyc_data_url',
                                              default="http://customerservice.sleepdev.renewbuy.in/v1/ckyc/get_customer_ckyc_data/"),
        "hdfc_ergo_payment_api_url": environ.get('hdfc_ergo_payment_api_url',
                                                 default='https://accessuat.hdfcergo.com/oem/INTEGRATION/API/Ampere/SubmitPayment'),
        "hdfc_ergo_ckyc_api_url": environ.get('hdfc_ergo_ckyc_api_url',
                                              default='https://ekyc-uat.hdfcergo.com/e-kyc/partner/binary'),
        "hdfc_ergo_ckyc_status_api_url": environ.get('hdfc_ergo_ckyc_status_api_url',
                                                     default='https://ekyc-uat.hdfcergo.com/e-kyc/primary/kyc-status/'),
        "proxy_server": environ.get('proxy_server', default='')
    },

    "zgil": {
        "zuno_auth_api_url": environ.get('zuno_auth_api_url',
                                         default='https://devapi.edelweissinsurance.com/oauth2/token'),
        "zuno_proposal_api_url": environ.get('zuno_proposal_api_url',
                                             default='https://devapi.edelweissinsurance.com/renewbuy/proposal/pc'),
        "policy_summary_api_url": environ.get('policy_summary_api_url',
                                              default="http://dataverse.sleepdev.renewbuy.in/api/v1/policy_summary/?"),
        "customer_ckyc_data_url": environ.get('customer_ckyc_data_url',
                                              default="http://customerservice.sleepdev.renewbuy.in/v1/ckyc/get_customer_ckyc_data/"),
        "zuno_payment_api_url": environ.get('zuno_payment_api_url',
                                            default='https://devapi.edelweissinsurance.com/renewbuy/payment'),
        "zuno_ckyc_api_url": environ.get('zuno_ckyc_api_url',
                                         default='https://uat.universalsompo.in/CKYC_API/api/Ampere/CKYC/searchDownload'),
        "zuno_ckyc_status_api_url": environ.get('zuno_ckyc_status_api_url',
                                                default='https://uat.universalsompo.in/CKYC_API/api/Ampere/CKYC/enquiry'),
        "zuno_auth_api_username": environ.get('zuno_auth_api_username', default='5i8m1h48vsnv6qlotn3h3s7fa4'),
        "zuno_auth_api_password": environ.get('zuno_auth_api_password', default='1h84837dtk6b7dr1eti96ego6m3he3e007p3a72u0ttabs9gce9b'),
        "zuno_auth_api_key": environ.get('zuno_auth_api_key', default='6vjZfZqe971dPyGsTfPSr1Np7PcGQAljpUJHytHj'),
        "zuno_auth_api_ckyc_username": environ.get('zuno_auth_api_ckyc_username', default='2r9a4a9lpvj2lp5bqbo0jhcp0l'),
        "zuno_auth_api_ckyc_password": environ.get('zuno_auth_api_ckyc_password', default='1q0fbp68juvm8f221f9ckh9j7i3ktq2hkibfk88q460pvccsfmqs'),
        "zuno_auth_ckyc_api_key": environ.get('zuno_auth_ckyc_api_key', default='vmX0qzSwUy5i4dyKa0MhuaQhQ6PECsp3FqZvwRX8'),
    }

}
