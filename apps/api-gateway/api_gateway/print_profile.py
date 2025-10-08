"""
打印当前档位与建议的 vLLM 启动命令
"""

from api_gateway.config import detect_gpu_memory, get_profile_name, load_profiles, settings


def main():
    """打印档位信息"""
    profile_name = get_profile_name(settings)
    profiles = load_profiles()
    gpu_mem = detect_gpu_memory()

    print("=" * 60)
    print("CxyGPT 当前配置档位")
    print("=" * 60)
    print()

    print(f"检测到显存: {gpu_mem}GB" if gpu_mem else "显存检测失败（可能未安装 pynvml）")
    print(f"当前档位: {profile_name}")
    print(f"模式: {'单人家用' if settings.SINGLE_USER else '多人并发'}")
    print()

    if profile_name not in profiles:
        print("⚠️  档位配置未找到，请检查 configs/profiles.yaml")
        return

    profile = profiles[profile_name]

    print("-" * 60)
    print("网关配置:")
    print("-" * 60)
    gateway_config = profile.get("gateway", {})
    for key, value in gateway_config.items():
        print(f"  {key}: {value}")
    print()

    print("-" * 60)
    print("vLLM 配置:")
    print("-" * 60)
    vllm_config = profile.get("vllm", {})
    for key, value in vllm_config.items():
        print(f"  {key}: {value}")
    print()

    print("-" * 60)
    print("建议的 vLLM 启动命令:")
    print("-" * 60)
    print()

    # 构建启动命令
    cmd = "python -m vllm.entrypoints.openai.api_server \\\n"
    cmd += "  --model ~/models/Qwen3-14B \\\n"
    cmd += f"  --served-model-name {settings.DEFAULT_MODEL} \\\n"

    for key, value in vllm_config.items():
        flag = key.replace("_", "-")
        cmd += f"  --{flag} {value} \\\n"

    cmd += "  --host 0.0.0.0 \\\n"
    cmd += "  --port 8000"

    print(cmd)
    print()

    # 提示
    if profile_name in ["SINGLE_32G", "DEV_32G"]:
        print("💡 提示:")
        if profile_name == "SINGLE_32G":
            print("  - 单人模式，使用全精度 bfloat16，质量优先")
            print("  - 无限流保护，适合家用场景")
        else:
            print("  - 多人模式，建议使用量化模型（GPTQ/AWQ 4bit）")
            print("  - 启用限流与队列保护，适合并发测试")
            print("  - 模型路径示例：~/models/Qwen3-14B-GPTQ-Int4")

    print()
    print("=" * 60)


if __name__ == "__main__":
    main()
