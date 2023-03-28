import inspect
import threading
from contextlib import contextmanager


class TimeoutLock:
    def __init__(self, logger, modul=None, timeout=10, debug=False, warning=True):
        self.logger = logger
        if modul is None:
            self.modul = f"{self.__class__.__name__}"
        else:
            self.modul = f"***Lock-{modul}"
        self.modul_f = "not set"
        self.timeout = timeout
        self.debug = debug
        self.warning = warning
        self._lock = threading.Lock()

    def update_variables(self, timeout=None, debug=None, warning=None):
        if timeout is not None:
            self.timeout = timeout
        if debug is not None:
            self.debug = debug
        if warning is not None:
            self.warning = warning

    @contextmanager
    def cm_acquire(self, timeout=None, debug=None, warning=None):
        self.modul_f = self.modul + f"->{inspect.stack()[2][3]}"
        result = self.acquire(timeout, debug, warning)
        yield result
        if result:
            self.release()

    def acquire(self, timeout=None, debug=None, warning=None):
        self.update_variables(timeout, debug, warning)
        if self.debug:
            self.logger.debug(f"{self.modul_f}: Try to acquire lock!")
        result = self._lock.acquire(blocking=True, timeout=self.timeout)
        if result is False and self.warning:
            self.logger.warning(f"{self.modul_f}: Couldn't acquired lock!")
        return result

    def release(self, debug=None, warning=None):
        self.update_variables(debug=debug, warning=warning)
        try:
            self._lock.release()
            if self.debug:
                self.logger.debug(f"{self.modul_f}: Released lock!")
        except RuntimeError:
            if self.warning:
                self.logger.warning(f"{self.modul_f}: Couldn't release lock, because no present lock!")
