"""
配置管理模块
"""

import os
from pathlib import Path
from typing import Any

import yaml
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """应用配置"""

    # 模式与档位
    SINGLE_USER: bool = True
    FORCE_PROFILE: str | None = None

    # 上游配置
    UPSTREAM_OPENAI_BASE: str = "http://127.0.0.1:8000"
    DEFAULT_MODEL: str = "qwen3-14b"
    USE_MOCK: bool = False

    # 服务端口
    GATEWAY_HOST: str = "0.0.0.0"
    GATEWAY_PORT: int = 8001

    # 数据库配置
    DATABASE_URL: str = "mysql+aiomysql://root:123456@localhost:3306/cxygpt?charset=utf8mb4"

    # Admission 限制
    MAX_INPUT_TOKENS: int = 3072
    MAX_OUTPUT_TOKENS: int = 512

    # 限流配置
    RATE_QPS: int = 0  # 0 = 不限
    RATE_TPM: int = 0

    # 队列与超时
    QUEUE_SIZE: int = 1
    TIMEOUT_FIRST_TOKEN: int = 20
    TIMEOUT_TOTAL: int = 120

    # 降级开关
    AUTO_DEGRADE: bool = False

    # 日志
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


def load_profiles() -> dict[str, Any]:
    """加载显存分档配置"""
    config_path = Path(__file__).parents[3] / "configs" / "profiles.yaml"

    if not config_path.exists():
        return {}

    with open(config_path, encoding="utf-8") as f:
        data = yaml.safe_load(f)
        return data.get("profiles", {})


def detect_gpu_memory() -> int | None:
    """检测显存大小（GB）"""
    try:
        import pynvml

        pynvml.nvmlInit()
        handle = pynvml.nvmlDeviceGetHandleByIndex(0)
        info = pynvml.nvmlDeviceGetMemoryInfo(handle)
        memory_gb = info.total / (1024**3)
        pynvml.nvmlShutdown()
        return int(memory_gb)
    except Exception:
        return None


def get_profile_name(settings: Settings) -> str:
    """获取当前档位名称"""
    if settings.FORCE_PROFILE:
        return settings.FORCE_PROFILE

    if settings.SINGLE_USER:
        gpu_mem = detect_gpu_memory()
        if gpu_mem and 30 <= gpu_mem <= 34:
            return "SINGLE_32G"
        return "SINGLE_32G"  # 默认

    # 多人模式
    gpu_mem = detect_gpu_memory()
    if not gpu_mem:
        return "DEV_32G"

    if 30 <= gpu_mem <= 34:
        return "DEV_32G"
    elif 46 <= gpu_mem <= 50:
        return "SRV_48G"
    elif 78 <= gpu_mem <= 82:
        return "SRV_80G"
    elif gpu_mem >= 140:
        return "SRV_MULTI_80G"

    return "DEV_32G"


def apply_profile(settings: Settings) -> Settings:
    """应用档位配置"""
    profiles = load_profiles()
    profile_name = get_profile_name(settings)

    if profile_name not in profiles:
        return settings

    profile = profiles[profile_name]
    gateway_config = profile.get("gateway", {})

    # 合并配置（环境变量优先级更高）
    for key, value in gateway_config.items():
        env_key = key.upper()
        if not os.getenv(env_key):  # 仅当环境变量未设置时应用档位配置
            setattr(settings, env_key, value)

    return settings


# 全局配置实例
settings = Settings()
settings = apply_profile(settings)
