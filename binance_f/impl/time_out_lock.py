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
        self.timeout = timeout
        self.debug = debug
        self.warning = warning
        self._lock = threading.Lock()

    def _set_variables(self, **kwargs):
        timeout = kwargs.get('timeout')
        timeout = timeout if timeout is not None else self.timeout
        debug = kwargs['debug'] if kwargs['debug'] is not None else self.debug
        warning = kwargs['warning'] if kwargs['warning'] is not None else self.warning
        return timeout, debug, warning

    def _build_modul_f(self, modul_f, func):
        if modul_f:
            return modul_f
        else:
            func = func if func else f"{inspect.stack()[3][3]}"
            return self.modul + f"->" + func

    @contextmanager
    def cm_acquire(self, timeout=None, debug=None, warning=None, func=None):
        modul_f = self._build_modul_f(None, func)
        result = self.acquire(timeout, debug, warning, func, modul_f)
        yield result
        if result:
            self.release(debug, warning, func, modul_f)

    def acquire(self, timeout=None, debug=None, warning=None, func=None, modul_f=None):
        modul_f = self._build_modul_f(modul_f, func)
        timeout, debug, warning = self._set_variables(timeout=timeout, debug=debug, warning=warning)
        if debug:
            self.logger.debug(f"{modul_f}: Try to acquire lock!")
        result = self._lock.acquire(blocking=True, timeout=timeout)
        if result is False and warning:
            self.logger.warning(f"{modul_f}: Couldn't acquired lock!")
        return result

    def release(self, debug=None, warning=None, func=None, modul_f=None):
        modul_f = self._build_modul_f(modul_f, func)
        _, debug, warning = self._set_variables(debug=debug, warning=warning)
        try:
            self._lock.release()
            if debug:
                self.logger.debug(f"{modul_f}: Released lock!")
        except RuntimeError:
            if warning:
                self.logger.warning(f"{modul_f}: Couldn't release lock, because no present lock!")
