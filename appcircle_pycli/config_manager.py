import os
import json
from pathlib import Path


class ConfigManager:
    def __init__(self):
        self.config_path = Path(os.path.expanduser("~")) / ".appcircle" / "config.json"
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.config_path.exists():
            self._create_default_config()

    def _load_config(self):
        if self.config_path.exists():
            with open(self.config_path, "r") as f:
                return json.load(f)
        else:
            return self._create_default_config()

    def _create_default_config(self):
        default_config = {
            "current": "default",
            "envs": {
                "default": {
                    "API_HOSTNAME": "https://api.appcircle.io",
                    "AUTH_HOSTNAME": "https://auth.appcircle.io",
                    "AC_ACCESS_TOKEN": None,
                }
            },
        }
        self._save_config(default_config)
        return default_config

    def _save_config(self, config):
        with open(self.config_path, "w") as f:
            json.dump(config, f, indent=2)

    def get_config(self):
        return self._load_config()

    def set_config(self, config):
        self._save_config(config)
