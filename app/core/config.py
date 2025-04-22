from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Settings for the application."""

    TEST: str
    ENV: str

    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_SERVER: str
    POSTGRES_PORT: str
    TEST_DB_URL: str

    # Firebase Web SDK
    FIREBASE_API_KEY: str
    FIREBASE_AUTH_DOMAIN: str
    FIREBASE_PROJECT_ID: str
    FIREBASE_STORAGE_BUCKET: str
    FIREBASE_MESSAGING_SENDER_ID: str
    FIREBASE_APP_ID: str
    FIREBASE_MEASUREMENT_ID: str

    # Firebase Admin SDK
    FIREBASE_TYPE: str
    FIREBASE_PRIVATE_KEY_ID: str
    FIREBASE_PRIVATE_KEY: str
    FIREBASE_CLIENT_EMAIL: str
    FIREBASE_CLIENT_ID: str
    FIREBASE_AUTH_URI: str
    FIREBASE_TOKEN_URI: str
    FIREBASE_AUTH_PROVIDER_CERT_URL: str
    FIREBASE_CLIENT_CERT_URL: str
    FIREBASE_UNIVERSE_DOMAIN: str

    class Config:
        env_file = ".env"


settings = Settings()
