import inspect
import threading
from contextlib import contextmanager


class TimeoutLock:
    def __init__(self, logger, modul=None, timeout=10, warning=True, debug=False):
        self.logger = logger
        if modul is None:
            self.modul = f"{self.__class__.__name__}"
        else:
            self.modul = f"***Lock-{modul}"
        self.modul_f = "not set"
        self.timeout = timeout
        self.warning = warning
        self.debug = debug
        self._lock = threading.Lock()

    @contextmanager
    def cm_acquire(self, timeout=None, warning=None):
        self.modul_f = self.modul + f"->{inspect.stack()[2][3]}"
        result = self.acquire(timeout, warning)
        yield result
        if result:
            self.release()

    def acquire(self, timeout=None, warning=None):
        if not timeout:
            timeout = self.timeout
        if not warning:
            warning = self.warning

        if self.debug:
            self.logger.debug(f"{self.modul_f}: Try to acquire lock!")
        result = self._lock.acquire(blocking=True, timeout=timeout)
        if result and self.debug:
            self.logger.debug(f"{self.modul_f}: Acquired lock!")
        if result is False and (warning or self.debug):
            self.logger.warning(f"{self.modul_f}: Couldn't acquired lock!")
        return result

    def release(self):
        try:
            if self.debug:
                self.logger.debug(f"{self.modul_f}: Try to release lock!")
            self._lock.release()
            if self.debug:
                self.logger.debug(f"{self.modul_f}: Released lock!")
        except RuntimeError:
            self.logger.warning(f"{self.modul_f}: Couldn't release lock, because no present lock!")
