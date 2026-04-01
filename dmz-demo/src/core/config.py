from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    it_server_opcua_url: str = "opc.tcp://it_server:4840/"
    ot_server_opcua_url: str = "opc.tcp://plc-server:4840"
    log_level: str = "INFO"

    it_server_redis_host: str = "10.10.30.101"
    it_server_redis_port: str = "6379"

    ot_forwarder_redis_host: str = "10.10.30.101"
    ot_forwarder_redis_port: str = "6379"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
