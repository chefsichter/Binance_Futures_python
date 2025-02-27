import threading
import logging

from apscheduler.events import EVENT_JOB_MISSED, EVENT_JOB_ERROR, EVENT_JOB_MAX_INSTANCES
from apscheduler.schedulers.blocking import BlockingScheduler
from binance_f.impl.websocketconnection import ConnectionState
from binance_f.impl.utils.timeservice import get_current_timestamp


def watch_dog_job(*args):
    watch_dog_instance = args[0]
    for connection in watch_dog_instance.connection_list:
        with connection.lock.cm_acquire(debug=False):
            if connection.state in [ConnectionState.CONNECTING, ConnectionState.CONNECTED]:
                if watch_dog_instance.is_auto_connect:
                    ts = get_current_timestamp() - connection.last_receive_time
                    if ts > connection.receive_limit_ms:
                        watch_dog_instance.logger.warning(connection.name + ": No response from server")
                        connection.set_to_reconnect_in_delay(watch_dog_instance.connection_delay_failure)
            elif connection.state == ConnectionState.IN_DELAY:
                connection.re_connect_in_delay()
            elif connection.state == ConnectionState.CLOSED_ON_ERROR:
                if watch_dog_instance.is_auto_connect:
                    connection.set_to_reconnect_in_delay(watch_dog_instance.connection_delay_failure)


class WebSocketWatchDog(threading.Thread):
    mutex = threading.Lock()
    connection_list = list()

    def __init__(self, is_auto_connect=True, receive_limit_ms=60000,
                 connection_delay_failure=15, check_conn_freq=5):
        # check_conn_freq: check all connections every 5 seconds, through watchdog
        threading.Thread.__init__(self)
        self.modul = f"{self.__class__.__name__}"
        self.is_auto_connect = is_auto_connect
        self.receive_limit_ms = receive_limit_ms
        self.connection_delay_failure = connection_delay_failure
        self.logger = logging.getLogger("binance-futures")
        self.scheduler = BlockingScheduler()
        self.scheduler.add_job(watch_dog_job, "interval", max_instances=1, seconds=check_conn_freq, args=[self])
        self.scheduler.add_listener(self.job_listener, EVENT_JOB_ERROR | EVENT_JOB_MISSED | EVENT_JOB_MAX_INSTANCES)
        self.start()

    def job_listener(self, event):
        job_str = f"{event.job_id[:10]}..."
        if event.code == EVENT_JOB_ERROR:
            self.logger.error(f"A job ({job_str}) crashed: " + "\n" + event.traceback + str(event.exception) + "\n")
        elif event.code == EVENT_JOB_MISSED:
            self.logger.error(f"A job ({job_str}) was missed.")
        elif event.code == EVENT_JOB_MAX_INSTANCES:
            self.logger.error(f"A job ({job_str}) was skipped.")

    def run(self):
        self.scheduler.start()

    def on_connection_created(self, connection):
        self.mutex.acquire()
        self.connection_list.append(connection)
        self.mutex.release()

    def on_connection_closed(self, connection):
        self.mutex.acquire()
        try:
            self.connection_list.remove(connection)
        except ValueError:
            self.logger.warning(f"{self.modul}: A non existing connection from {self.modul} was tried to be removed.")
        self.mutex.release()
