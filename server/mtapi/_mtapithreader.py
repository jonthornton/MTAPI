import threading, time, datetime, logging


logger = logging.getLogger(__name__)

class _MtapiThreader(object):

    LOCK_TIMEOUT = 300
    update_lock = threading.Lock()
    update_lock_time = datetime.datetime.now()

    def __init__(self, mtapi, expires_seconds=60):
        self.mtapi = mtapi
        self.EXPIRES_SECONDS = expires_seconds

    def start_timer(self):
        '''Start a long-lived thread to loop infinitely and trigger updates at
        some regular interval.'''

        logger.info('Starting update thread...')
        self.timer_thread = threading.Thread(target=self.update_timer)
        self.timer_thread.daemon = True
        self.timer_thread.start()

    def update_timer(self):
        '''This method runs in its own thread. Run feed updates in short-lived
        threads.'''
        while True:
            time.sleep(self.EXPIRES_SECONDS)
            self.update_thread = threading.Thread(target=self.locked_update)
            self.update_thread.start()

    def locked_update(self):
        if not self.update_lock.acquire(False):
            logger.info('Update locked!')

            lock_age = datetime.datetime.now() - self.update_lock_time
            if lock_age.total_seconds() < self.LOCK_TIMEOUT:
                return
            else:
                self.update_lock = threading.Lock()
                logger.warn('Cleared expired update lock')

        self.update_lock_time = datetime.datetime.now()

        self.mtapi._update()
        self.mtapi._bus_update()

        self.update_lock.release()

    def restart_if_dead(self):
        if not self.timer_thread.is_alive():
            logger.warn('Timer died')
            self.start_timer()
            return True

        return False
