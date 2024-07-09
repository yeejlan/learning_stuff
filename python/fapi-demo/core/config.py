import os
from typing import List
from dotenv import load_dotenv

class Config:
    def __init__(self, env_file: str ='.env'):
        load_dotenv(env_file)
        self._cache = {}

    def get(self, key: str, default: str = '') -> str:
        if key not in self._cache:
            self._cache[key] = os.getenv(key) or default
        return self._cache[key]

    def getInt(self, key: str, default: int = 0) -> int:
        value = self.get(key, str(default))
        try:
            return int(value)
        except ValueError:
            return default

    def getFloat(self, key: str, default: float = 0.0) -> float:
        value = self.get(key, str(default))
        try:
            return float(value)
        except ValueError:
            return default

    def getBool(self, key: str, default: bool = False) -> bool:
        value = self.get(key, str(default)).lower()
        if value in ['true', 'yes', '1', 'on']:
            return True
        elif value in ['false', 'no', '0', 'off']:
            return False
        return default

    def getList(self, key: str, default: List[str] = []) -> List[str]:
        value = self.get(key, '')
        if value:
            return [item.strip() for item in value.split(',')]
        return default.copy() if default else []

    def refresh(self):
        self._cache.clear()

class ConfigManager:
    def __init__(self):
        self._config = None

    @property
    def config(self) -> Config:
        if self._config is None:
            self._config = Config()
        return self._config

config_manager = ConfigManager()

def getConfig() -> Config:
    return config_manager.config

if __name__ == "__main__":
    config = getConfig()

    db_host = config.get('DB_HOST', 'localhost')
    db_port = config.getInt('DB_PORT', 3306)
    use_ssl = config.getBool('USE_SSL', False)
    allowed_ips = config.getList('ALLOWED_IPS', ['127.0.0.1'])

    out = (db_host, db_port, use_ssl, allowed_ips)
    print(out)