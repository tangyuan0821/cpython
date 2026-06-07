from __future__ import annotations

import argparse
import asyncio
import contextvars
import statistics
import sys
import time


def callback(fut: asyncio.Future[None]) -> None:
    pass


def bench_add_done_callback(count: int) -> float:
    loop = asyncio.new_event_loop()
    ctx = contextvars.copy_context()
    try:
        fut = loop.create_future()
        fut.add_done_callback(callback, context=ctx)
        fut.add_done_callback(callback, context=ctx)

        start = time.perf_counter_ns()
        for _ in range(count):
            fut.add_done_callback(callback, context=ctx)
        return (time.perf_counter_ns() - start) / 1e9
    finally:
        loop.close()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--count", type=int, default=1_000_000)
    parser.add_argument("--trials", type=int, default=15)
    parser.add_argument("--warmup", type=int, default=3)
    args = parser.parse_args()

    for _ in range(args.warmup):
        bench_add_done_callback(args.count)

    timings = [bench_add_done_callback(args.count) for _ in range(args.trials)]
    best = min(timings)
    median = statistics.median(timings)
    mean = statistics.fmean(timings)
    stdev = statistics.pstdev(timings)

    print(sys.version.replace("\n", " "))
    print(f"count: {args.count}")
    print(
        f"best: {best * 1e3:.3f} ms; "
        f"median: {median * 1e3:.3f} ms; "
        f"mean: {mean * 1e3:.3f} ms; "
        f"stdev: {stdev * 1e3:.3f} ms"
    )
    print(f"callbacks/sec at best: {args.count / best:.3f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
