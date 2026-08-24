import time
from collections import defaultdict
from threading import Lock

from app.utils.exceptions import TooManyRequestsException

MAX_ATTEMPTS = 5
WINDOW_SECONDS = 300

_attempts: dict[str, list[float]] = defaultdict(list)
_lock = Lock()


def check_rate_limit(key: str) -> None:
    now = time.time()
    with _lock:
        attempts = _attempts[key]
        attempts[:] = [t for t in attempts if now - t < WINDOW_SECONDS]

        if len(attempts) >= MAX_ATTEMPTS:
            raise TooManyRequestsException(
                f"Nhập sai nhiều lần. Quay lại sau {WINDOW_SECONDS // 60} phut"
            )

        attempts.append(now)