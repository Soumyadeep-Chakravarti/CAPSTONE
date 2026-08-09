from dataclasses import dataclass
import os


@dataclass(frozen=True)
class DWHConfig:
    host: str = os.getenv("DWH_HOST", "localhost")
    port: int = int(os.getenv("DWH_PORT", "5433"))
    database: str = os.getenv("DWH_DATABASE", "parking_dw")
    user: str = os.getenv("DWH_USER", "warehouse")
    password: str = os.getenv("DWH_PASSWORD", "warehouse_dev")

    @property
    def url(self) -> str:
        return (
            f"postgresql+psycopg://"
            f"{self.user}:{self.password}"
            f"@{self.host}:{self.port}"
            f"/{self.database}"
        )
