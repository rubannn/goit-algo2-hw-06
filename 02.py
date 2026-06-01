import json
from pathlib import Path
from time import perf_counter

from datasketch import HyperLogLog

def get_time(function):
    def wrapper(*args, **kwargs) -> tuple[int, float]:
        start_time = perf_counter()
        result = function(*args, **kwargs)
        elapsed_time = perf_counter() - start_time
        return result, elapsed_time

    return wrapper


def iter_ip_addresses(log_path: Path):
    with open(log_path, "r", encoding="utf-8") as file:
        for line in file:
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue

            ip = record.get("remote_addr")
            if ip:
                yield ip


@get_time
def count_unique_ips(log_path: Path):
    unique_ips = set(iter_ip_addresses(log_path))
    return len(unique_ips)


@get_time
def hyperlog_count_unique_ips(log_path: Path, precision: int = 14):
    hyperloglog = HyperLogLog(p=precision)
    for ip in iter_ip_addresses(log_path):
        hyperloglog.update(ip.encode("utf-8"))
    return round(hyperloglog.count())


def print_results(
    m_count: int, m_time: float,
    hl_count: int, hl_time: float,
) -> None:
    print("Результати порівняння:")
    print(f"{'':24}{'Точний підрахунок':>20}{'HyperLogLog':>16}")
    print(f"{'Унікальні елементи':24}{m_count:>20}{hl_count:>16}")
    print(f"{'Час виконання (сек.)':24}{m_time:>20.6f}{hl_time:>16.6f}")


if __name__ == "__main__":
    log_file_path = Path(__file__).resolve().parent / "data" / "lms-stage-access.log"

    print_results(
        *count_unique_ips(log_file_path),
        *hyperlog_count_unique_ips(log_file_path)
    )
