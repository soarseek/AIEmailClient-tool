import os
from typing import Dict

ENV_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')

def load_env_config() -> Dict[str, str]:
    config = {}
    if os.path.exists(ENV_FILE):
        with open(ENV_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    if '=' in line:
                        key, value = line.split('=', 1)
                        config[key.strip()] = value.strip()
    return config

def save_env_config(config: Dict[str, str]) -> None:
    with open(ENV_FILE, 'w', encoding='utf-8') as f:
        f.write('# SMTP配置\n')
        f.write(f'SMTP_SERVER={config.get("SMTP_SERVER", "smtp.qq.com")}\n')
        f.write(f'SMTP_PORT={config.get("SMTP_PORT", "587")}\n')
        f.write(f'SMTP_USERNAME={config.get("SMTP_USERNAME", "")}\n')
        f.write(f'SMTP_PASSWORD={config.get("SMTP_PASSWORD", "")}\n')

def get_default_config() -> Dict[str, str]:
    return {
        'SMTP_SERVER': 'smtp.qq.com',
        'SMTP_PORT': '587',
        'SMTP_USERNAME': '',
        'SMTP_PASSWORD': ''
    }