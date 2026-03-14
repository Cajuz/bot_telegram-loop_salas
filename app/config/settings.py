from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Bot
    TELEGRAM_TOKEN: str = "TOKEN_AQUI"
    OWNER_ID: str = "0"
    OWNER2_ID: str = "0"
    NOTIF_ID: str = "0"
    LOG_VENDAS_CHAT_ID: str = "0"

    # API Free Fire
    FREEFIRE_BASE_URL: str = "https://salasff.com.br"
    FREEFIRE_OAUTH_KEY: str = "FFSL-XXXXXXXX"

    # Wallet PIX
    WALLET_URL: str = "https://wallet.stormapplications.com/api/v1"
    WALLET_API_KEY: str = "sk_live_xxxx"

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./data/salasff.db"

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"          # ← essa linha resolve o erro



settings = Settings()
