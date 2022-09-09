from threading import Timer
from simulators.backend.genericbackend import (
    GenericBackendSystem,
    BackendError,
)


class System(GenericBackendSystem):

    commands = {
        'setup': 'do_setup',
    }
    commands.update(GenericBackendSystem.commands)

    def __init__(self, setup_time=60):
        GenericBackendSystem.__init__(self)
        self._waiting_for_setup_time = False
        self.setup_time = setup_time
        self._setupID = None
        self.ready = False  # Is the system ready to operate?
        self.tasks = {
            'acquisition': self.acquiring,  # From generic backend
            'setup': False,
        }

    def system_stop(self):
        if self._setupID:
            self._setupID.cancel()
            self._setupID.join()
        return super().system_stop()

    def _running_task(self):
        running_task = ''
        for task, is_running in self.tasks.items():
            if is_running:
                running_task = task
        return running_task

    def do_setup(self, _):
        if any(self.tasks.values()):
            raise BackendError(f'{self._running_task()} is still running')
        self.tasks['setup'] = True
        self._setupID = Timer(self.setup_time, self._setup)
        self._setupID.start()

    def _setup(self):
        self.ready = True
        self.tasks['setup'] = False

    @property
    def status_msg(self):
        if any(self.tasks.values()):
            return f'{self._running_task()} in progress'
        elif not self.ready:
            return 'system not initialized (setup required)'
        else:
            return 'no task is running'

    def do_status(self, _):
        return (
            self._get_time(),
            self.status_msg,
            1 if self.acquiring else 0
        )
