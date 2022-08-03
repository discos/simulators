from __future__ import division, with_statement
import time
import operator
from multiprocessing import Value, Lock
from threading import Timer
from simulators.mscu.parameters import closers, app_nr, axes, stow_position


class DriveCabinet:
    cab_state = {
        'ready': 0,           # The servo ready to move
        'starting': 1,        # The servo is performing a setup
        'block_removed': 2,   # A setup is required
        'stow': 3,            # Parked
        'power_failure': 4,   # Power supply failure
        'disable': 5,         # Disabled from other drive cabinet
        'reset_required': 6,  # A clearemergency is required
        'blocked': 7,         # Blocking condition
    }

    app_state = {}
    app_status = {}

    def __init__(self):
        self.cab_state = Value('i', DriveCabinet.cab_state['stow'])

    def set_state(self, state):
        try:
            self.cab_state.value = DriveCabinet.cab_state[state]
        except KeyError:
            pass


class Servo:

    def __init__(self, address):
        self.id = address
        self.name = app_nr[self.id]  # GRF, PFP, SRP, M3R
        self.axes = axes[self.name]  # Number of axes
        self.stow_position = stow_position[self.name]
        self.history = History(self.axes)
        self.dc = DriveCabinet()
        self.stow(0)
        self.setpos_NAK = False
        self.dc_thread = None

    def stop(self):
        if self.dc_thread:
            self.dc_thread.cancel()
            self.dc_thread.join()

    def getpos(self, cmd_num):
        data = self.history.get()
        answer = f'?getpos:{cmd_num}={self.id}> {Servo.ctime()}'
        # Read the position stored in a shelve db by a setpos command
        for position in data[1:]:
            answer += f',{position}'
        answer += closers[0]
        return [answer]

    def getappstatus(self, cmd_num):
        value = '0000030D'
        answer = f'?getappstatus:{cmd_num}={self.id}> {value}'
        return [answer + closers[0]]

    def getstatus(self, cmd_num):
        app_state = 4  # remote auto
        app_status = "FFFF"  # Everything OK
        cab_state = self.dc.cab_state.value

        answer = f'?getstatus:{cmd_num}={self.id}> '
        answer += f'{Servo.ctime()},{app_state},{app_status},{cab_state}'

        # Read the position stored in a shelve db by a setpos command
        data = self.history.get()
        for position in data[1:]:
            answer += f',{position}'
        answer += closers[0]
        return [answer]

    def setpos(self, cmd_num, *params):
        if self.setpos_NAK or len(params) != self.axes + 3:
            answer = f'!NAK_setpos:{cmd_num}={self.id}'
            params = ['cannot set the position']
        else:
            timestamp, position = params[0], list(params[-self.axes:])
            self.history.insert(position, timestamp)
            answer = f'@setpos:{cmd_num}={self.id}'

        for param in params:
            answer += f",{param}"
        answer += closers[0]
        return [answer.replace('@', '?'), answer]

    def setup(self, cmd_num, *params):
        answer = f'@setup:{cmd_num}={self.id}'
        for param in params:
            answer += f",{param}"
        answer += closers[0]
        self.dc.set_state('starting')

        if self.dc_thread:
            self.dc_thread.cancel()

        self.dc_thread = Timer(
            3,  # The setup takes 3 seconds
            function=self.dc.set_state,
            args=('ready',)
        )
        self.dc_thread.start()
        return [answer.replace('@', '?'), answer]

    def stow(self, cmd_num, *params):
        answer = f'@stow:{cmd_num}={self.id}'
        for param in params:
            answer += f",{param}"
        answer += closers[0]
        self.dc.cab_state.value = DriveCabinet.cab_state['stow']
        self.history.insert(self.stow_position)
        return [answer.replace('@', '?'), answer]

    def disable(self, cmd_num, *params):
        answer = f'@disable:{cmd_num}={self.id}'
        for param in params:
            answer += f",{param}"
        answer += closers[0]
        self.dc.cab_state.value = DriveCabinet.cab_state['stow']
        return [answer.replace('@', '?'), answer]

    def clean(self, cmd_num, *params):
        answer = f'@clean:{cmd_num}={self.id}'
        for param in params:
            answer += f",{param}"
        answer += closers[0]
        self.history.clean()
        return [answer.replace('@', '?'), answer]

    def getspar(self, cmd_num, *params):
        answer = f'?getspar:{cmd_num}={self.id}> '

        index_sub = list(params[-2:])
        if [1250, 0] == index_sub:  # Acceleration
            answer += '3'
        elif [1240, 0] == index_sub:  # Max speed
            answer += '10'
        else:
            # print('index_sub, type: ', index_sub, type(index_sub))
            answer += '0'

        answer += closers[0]
        return [answer]

    def setsdatbitb16(self, cmd_num, *params):
        answer = f'@setsdatbitb16:{cmd_num}={self.id}'
        for param in params:
            answer += f",{param}"
        answer += closers[0]
        return [answer]

    @staticmethod
    def ctime():
        """Return the current time in OMG format"""
        acstime_ACE_BEGIN = 122192928000000000
        return int(acstime_ACE_BEGIN + time.time() * 10000000)


class History:
    lock = Lock()

    def __init__(self, n_axes):
        self.n_axes = n_axes
        self.history = []
        self.insert(n_axes * [0])

    def insert(self, position, timestamp=None):
        target_time = timestamp if timestamp else Servo.ctime()
        data = [target_time] + list(position)
        with History.lock:
            self.history.append(data)
            self.history.sort(key=operator.itemgetter(0))
            self.history = self.history[-2 ** 15:]  # Last 2**15 positions

    def clean(self, since=0):
        target_time = since if since else Servo.ctime()
        with History.lock:
            idx = len(self.history)
            self.history.sort(key=operator.itemgetter(0))
            for idx, item in enumerate(self.history):
                timestamp = item[0]
                if timestamp > target_time:
                    break
            self.history = self.history[:idx]

    def get(self, target_time=None):
        """Returns the position at target_time
        as [timestamp, axisA, ..., axisN]"""
        if target_time is None:
            target_time = Servo.ctime()
        size = len(self.history)
        idx = -1
        with History.lock:
            while idx >= -size:
                current = self.history[idx]
                if target_time >= current[0]:
                    if idx < -1:  # We are between two entries, interpolate
                        nxt = self.history[idx + 1]
                        factor = float(target_time - current[0])
                        factor /= (nxt[0] - current[0])
                        response = [target_time]
                        for i in range(1, len(current)):
                            value = (1 - factor) * current[i] + factor * nxt[i]
                            response.append(value)
                        return response
                    else:  # First entry, return the values right away
                        return current
                idx -= 1
            return self.history[0]
