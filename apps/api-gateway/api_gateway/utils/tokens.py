"""
Token 估算工具
"""

import re


def estimate_tokens(text: str) -> int:
    """
    简单的 token 估算
    中文：~1.8 字符/token
    英文：~4 字符/token
    """
    if not text:
        return 0

    chinese_chars = len(re.findall(r"[\u4e00-\u9fa5]", text))
    other_chars = len(text) - chinese_chars

    return int(chinese_chars / 1.8 + other_chars / 4)


def estimate_messages_tokens(messages: list[dict[str, str]]) -> int:
    """估算消息列表总 token 数"""
    total = 0

    for msg in messages:
        # 每条消息约 4 token overhead
        total += 4
        total += estimate_tokens(msg.get("content", ""))

    # assistant 开始约 3 token
    return total + 3
