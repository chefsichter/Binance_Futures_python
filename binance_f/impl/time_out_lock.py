import threading
from contextlib import contextmanager


class TimeoutLock:
    def __init__(self, logger, modul=None, timeout=10, warning=True):
        self.logger = logger
        if modul is None:
            self.modul = f"{self.__class__.__name__}"
        else:
            self.modul = f"{modul}-TimeoutLock"
        self.timeout = timeout
        self.warning = warning
        self._lock = threading.Lock()

    @contextmanager
    def cm_acquire(self, timeout=None, warning=None):
        result = self.acquire(timeout, warning)
        yield result
        if result:
            self.release()

    def acquire(self, timeout=None, warning=None):
        if not timeout:
            timeout = self.timeout
        if not warning:
            warning = self.warning

        result = self._lock.acquire(blocking=True, timeout=timeout)
        if result is False and warning:
            self.logger.warning(f"{self.modul}: Couldn't acquired lock!")
        return result

    def release(self):
        try:
            self._lock.release()
        except RuntimeError:
            self.logger.warning(f"{self.modul}: Couldn't release lock, because no present lock!")
