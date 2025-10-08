"""
并发压测脚本

用法：
    python scripts/bench.py --concurrency 50 --rounds 100 --url http://127.0.0.1:8001/v1/chat/completions

输出：
    - 平均/P95 首 token 延迟
    - 平均/P95 总耗时
    - 错误率（413/429/503）
    - 吞吐量（RPS）
"""
import asyncio
import argparse
import time
import httpx
from typing import List, Dict, Any
import statistics


class BenchmarkStats:
    """统计信息"""

    def __init__(self):
        self.total = 0
        self.success = 0
        self.errors: Dict[int, int] = {}

        self.first_token_latencies: List[float] = []
        self.total_latencies: List[float] = []

    def add_result(
        self,
        success: bool,
        error_code: int = 0,
        first_token_latency: float = 0,
        total_latency: float = 0,
    ):
        """添加结果"""
        self.total += 1

        if success:
            self.success += 1
            self.first_token_latencies.append(first_token_latency)
            self.total_latencies.append(total_latency)
        else:
            self.errors[error_code] = self.errors.get(error_code, 0) + 1

    def print_summary(self, duration: float):
        """打印摘要"""
        print("\n" + "=" * 60)
        print("压测结果")
        print("=" * 60)

        print(f"\n总请求数: {self.total}")
        print(f"成功数: {self.success}")
        print(f"失败数: {self.total - self.success}")

        if self.errors:
            print("\n错误分布:")
            for code, count in sorted(self.errors.items()):
                print(f"  {code}: {count} 次 ({count/self.total*100:.1f}%)")

        if self.first_token_latencies:
            print(f"\n首 token 延迟:")
            print(f"  平均: {statistics.mean(self.first_token_latencies):.3f}s")
            print(f"  P50: {statistics.median(self.first_token_latencies):.3f}s")
            print(
                f"  P95: {statistics.quantiles(self.first_token_latencies, n=20)[18]:.3f}s"
            )
            print(f"  P99: {statistics.quantiles(self.first_token_latencies, n=100)[98]:.3f}s")

        if self.total_latencies:
            print(f"\n总耗时:")
            print(f"  平均: {statistics.mean(self.total_latencies):.3f}s")
            print(f"  P50: {statistics.median(self.total_latencies):.3f}s")
            print(f"  P95: {statistics.quantiles(self.total_latencies, n=20)[18]:.3f}s")
            print(f"  P99: {statistics.quantiles(self.total_latencies, n=100)[98]:.3f}s")

        print(f"\n吞吐量: {self.success / duration:.2f} RPS")
        print("=" * 60 + "\n")


async def single_request(url: str, stats: BenchmarkStats):
    """单个请求"""
    payload = {
        "model": "qwen3-14b",
        "messages": [{"role": "user", "content": "你好，请简单介绍一下你自己。"}],
        "stream": True,
        "max_tokens": 100,
    }

    start = time.time()
    first_token_time = None

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            async with client.stream("POST", url, json=payload) as response:
                if response.status_code != 200:
                    stats.add_result(False, error_code=response.status_code)
                    return

                async for line in response.aiter_lines():
                    if not line.strip():
                        continue

                    if first_token_time is None:
                        first_token_time = time.time()

                    if "data: [DONE]" in line:
                        break

        total_time = time.time() - start
        first_token_latency = (
            first_token_time - start if first_token_time else total_time
        )

        stats.add_result(
            True, first_token_latency=first_token_latency, total_latency=total_time
        )

    except Exception as e:
        stats.add_result(False, error_code=0)


async def benchmark(url: str, concurrency: int, rounds: int):
    """压测主函数"""
    stats = BenchmarkStats()

    print(f"开始压测:")
    print(f"  URL: {url}")
    print(f"  并发数: {concurrency}")
    print(f"  轮次: {rounds}")
    print(f"  总请求数: {concurrency * rounds}")
    print()

    start_time = time.time()

    for round_num in range(rounds):
        print(f"轮次 {round_num + 1}/{rounds}...")

        tasks = [single_request(url, stats) for _ in range(concurrency)]
        await asyncio.gather(*tasks)

    duration = time.time() - start_time

    stats.print_summary(duration)


def main():
    parser = argparse.ArgumentParser(description="CxyGPT API 压测工具")
    parser.add_argument(
        "--url",
        default="http://127.0.0.1:8001/v1/chat/completions",
        help="API 地址",
    )
    parser.add_argument("--concurrency", "-c", type=int, default=10, help="并发数")
    parser.add_argument("--rounds", "-r", type=int, default=10, help="轮次")

    args = parser.parse_args()

    asyncio.run(benchmark(args.url, args.concurrency, args.rounds))


if __name__ == "__main__":
    main()
