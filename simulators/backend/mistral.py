from threading import Timer
from simulators.backend.genericbackend import (
    GenericBackendSystem,
    BackendError,
)


class System(GenericBackendSystem):

    commands = {
        'setup': 'do_setup',
        'target-sweep': 'do_target_sweep',
        'vna-sweep': 'do_vna_sweep',
    }
    commands.update(GenericBackendSystem.commands)

    setup_time = 60
    sweep_time = 300

    def __init__(self):
        GenericBackendSystem.__init__(self)
        self._setupID = None
        self._target_sweepID = None
        self._vna_sweepID = None
        self._running_setup = False
        self._running_target_sweep = False
        self._running_vna_sweep = False
        self.ready = False  # Is the system ready to operate?

    def system_stop(self):
        if self._setupID:
            self._setupID.cancel()
            self._setupID.join()
        if self._target_sweepID:
            self._target_sweepID.cancel()
            self._target_sweepID.join()
        if self._vna_sweepID:
            self._vna_sweepID.cancel()
            self._vna_sweepID.join()
        return super().system_stop()

    @property
    def running_task(self):
        result = ''
        tasks = {
            'acquisition': self.acquiring,  # From generic backend
            'setup': self._running_setup,
            'target-sweep': self._running_target_sweep,
            'vna-sweep': self._running_vna_sweep,
        }
        for task, is_running in tasks.items():
            if is_running:
                result = task
        return result

    @property
    def error(self):
        result = {}
        if self.failure:
            result = {
                'reason': 'failure',
                'message': 'failure description'
            }
        elif running_task := self.running_task:
            result = {
                'reason': 'running_task',
                'message': f'{running_task} in progress'
            }
        elif not self.ready:
            result = {
                'reason': 'setup',
                'message': 'system not initialized (setup required)'
            }
        return result

    def do_setup(self, _):
        if error := self.error:
            if error['reason'] != 'setup':
                raise BackendError(error['message'])
        self._running_setup = True
        self._setupID = Timer(self.setup_time, self._setup)
        self._setupID.start()

    def _setup(self):
        self.ready = True
        self._running_setup = False

    def do_start(self, args):
        if error := self.error:
            raise BackendError(error['message'])
        super().do_start(args)

    def do_target_sweep(self, _):
        if error := self.error:
            raise BackendError(error['message'])
        self._running_target_sweep = True
        self._target_sweepID = Timer(self.sweep_time, self._target_sweep)
        self._target_sweepID.start()

    def _target_sweep(self):
        self._running_target_sweep = False

    def do_vna_sweep(self, _):
        if error := self.error:
            raise BackendError(error['message'])
        self._running_vna_sweep = True
        self._vna_sweepID = Timer(self.sweep_time, self._vna_sweep)
        self._vna_sweepID.start()

    def _vna_sweep(self):
        self._running_vna_sweep = False

    def do_status(self, _):
        return (
            self._get_time(),
            self.error.get('message') or 'ready to run a task',
            1 if self.acquiring else 0
        )
