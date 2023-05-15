import time
import re
import random
try:
    from scipy.interpolate import splrep, splev
except ImportError as ex:  # pragma: no cover
    raise ImportError('The `scipy` package, required for the simulator'
        + ' to run, is missing!') from ex
from threading import Lock
from bisect import bisect_left
from socketserver import ThreadingTCPServer
from simulators.common import ListeningSystem


# Each system module (like active_surface.py, acu.py, etc.) has to
# define a list called servers. This list contains tuples
# (l_address, s_address, kwargs). l_address is the tuple (ip, port) that
# defines the listening node that exposes the parse method, s_address
# is the tuple that defines the optional sending node that exposes the
# subscribe and unsibscribe methods, while kwargs is a dict of optional
# extra arguments.
servers = [(('0.0.0.0', 12800), (), ThreadingTCPServer, {})]


class System(ListeningSystem):

    tail = '\r\n'
    bad = 'OUTPUT:BAD'
    program_track_timegap = 0.2

    @property
    def good(self):
        return f'OUTPUT:GOOD,{self.plc_time()}'

    @staticmethod
    def plc_time():
        return f'{time.time():.6f}'

    commands = {
        'STATUS': '_status',
        'SETUP': '_setup',
        'STOW': '_stow',
        'STOP': '_stop',
        'PRESET': '_preset',
        'PROGRAMTRACK': '_programTrack',
        'OFFSET': '_offset'
    }

    configurations = {
        'Primario': {'ID': 1},
        'Gregoriano1': {'ID': 11},
        'Gregoriano2': {'ID': 12},
        'Gregoriano3': {'ID': 13},
        'Gregoriano4': {'ID': 14},
        'Gregoriano5': {'ID': 15},
        'Gregoriano6': {'ID': 16},
        'Gregoriano7': {'ID': 17},
        'Gregoriano8': {'ID': 18},
        'BWG1': {'ID': 21},
        'BWG2': {'ID': 22},
        'BWG3': {'ID': 23},
        'BWG4': {'ID': 24},
    }

    def __init__(self):
        self.msg = ''
        self.configuration = 0
        self.simulation = 1
        self.plc_version = 1
        self.control = 1
        self.power = 1
        self.emergency = 2
        self.enabled = 1
        self.last_executed_command = 0
        self.servos = {
            'PFP': PFP(),
            'SRP': SRP(),
            'M3R': M3R(),
            'GFR': GFR(),
            'DerotatoreGFR1': Derotator('GFR1'),
            'DerotatoreGFR2': Derotator('GFR2'),
            'DerotatoreGFR3': Derotator('GFR3'),
            'DerotatorePFP': Derotator('PFP'),
        }

    def parse(self, byte):
        self.msg += byte
        if self.msg.endswith(self.tail):
            msg = self.msg
            self.msg = ''
            return self._execute(msg)
        return True

    def _execute(self, msg):
        """This method parses and executes a command the moment it is
        completely received.

        :param msg: the received command, comprehensive of its header and tail.
        """
        args = [x.strip() for x in re.split('=|,', msg)]

        cmd = self.commands.get(args[0])
        if cmd is None:
            return self.bad + self.tail
        cmd = getattr(self, cmd)

        args = args[1:]
        return f'{cmd(args)}{self.tail}'

    def _status(self, args):
        if len(args) > 1:
            return self.bad
        if len(args) == 1:
            servo_id = args[0]
            if servo_id not in self.servos:
                return self.bad
            answer = self.good
            servo = self.servos.get(servo_id)
            answer += servo.get_status()
            return answer
        else:
            answer = self.good
            plc_time = answer.split(',')[-1]
            answer += f',CURRENT_CONFIG={self.configuration}|'
            answer += f'SIMULATION_ENABLED={self.simulation}|'
            answer += f'PLC_TIME={plc_time}|'
            answer += f'PLC_VERSION={self.plc_version}|'
            answer += f'CONTROL={self.control}|'
            answer += f'POWER={self.power}|'
            answer += f'EMERGENCY={self.emergency}|'
            answer += f'ENABLED={self.enabled}|'
            answer += f'LAST_EXECUTED_COMMAND={self.last_executed_command}'
            return answer

    def _setup(self, args):
        if len(args) != 1:
            return self.bad
        configuration = args[0]
        if configuration not in self.configurations:
            return self.bad
        self.configuration = self.configurations.get(configuration)['ID']
        for _, servo in self.servos.items():
            servo.operative_mode = 10  # SETUP
        self.last_executed_command = self.plc_time()
        return self.good

    def _stow(self, args):
        if len(args) != 2:
            return self.bad
        servo_id = args[0]
        if servo_id not in self.servos:
            return self.bad
        try:
            _ = int(args[1])  # STOW POSITION
        except ValueError:
            return self.bad
        servo = self.servos.get(servo_id)
        servo.operative_mode = 20  # STOW
        self.last_executed_command = self.plc_time()
        return self.good

    def _stop(self, args):
        if len(args) != 1:
            return self.bad
        servo_id = args[0]
        if servo_id not in self.servos:
            return self.bad
        servo = self.servos.get(servo_id)
        servo.operative_mode = 30  # STOP
        self.last_executed_command = self.plc_time()
        return self.good

    def _preset(self, args):
        if len(args) < 2:
            return self.bad
        servo_id = args[0]
        if servo_id not in self.servos:
            return self.bad
        servo = self.servos.get(servo_id)
        coords = args[1:]
        if len(coords) != servo.DOF:
            return self.bad
        try:
            for index, coord in enumerate(coords):
                coords[index] = float(coord)
        except ValueError:
            return self.bad
        servo.operative_mode = 40  # PRESET
        servo.set_coords(coords)
        self.last_executed_command = self.plc_time()
        return self.good

    def _programTrack(self, args):
        try:
            servo_id = args[0]
        except IndexError:
            return self.bad
        if servo_id not in self.servos:
            return self.bad
        servo = self.servos.get(servo_id)
        if not servo.program_track_capable:
            return self.bad
        if len(args) != 4 + servo.DOF:
            return self.bad
        try:
            trajectory_id = int(args[1])
            point_id = int(args[2])
            start_time = args[3]
            coords = args[4:]
            for coord in coords:
                coord = float(coord)
            if start_time == '*':
                if trajectory_id != servo.trajectory_id:
                    # New trajectory with no start time, error
                    return self.bad
                elif point_id != servo.trajectory_point_id + 1:
                    # Unexpected point_id
                    return self.bad
                start_time = servo.trajectory_start_time
            else:
                start_time = float(start_time)
                # Point is in the past
                if start_time < time.time():
                    return self.bad
                if point_id != 0:
                    # Wrong starting point_id
                    return self.bad
                # Initialize a new trajectory
                servo.trajectory_lock.acquire()
                servo.trajectory = [
                    [] for _ in range(servo.DOF + 1)
                ]
                servo.trajectory_id = trajectory_id
                servo.trajectory_start_time = start_time
                servo.trajectory_lock.release()

            servo.trajectory_lock.acquire()
            servo.trajectory_point_id = point_id
            servo.trajectory_lock.release()
            point_time = start_time
            point_time += point_id * self.program_track_timegap
            # Point is in the past
            if point_time < time.time():
                return self.bad
            # Everything seems correct, insert the point
            servo.trajectory_lock.acquire()
            servo.trajectory[0].append(point_time)
            for index in range(servo.DOF):
                servo.trajectory[index + 1].append(coords[index])

            # Delete points older than 1 second before the current time
            pt_index = bisect_left(
                servo.trajectory[0],
                time.time() - 1
            )
            for index, trajectory in enumerate(servo.trajectory):
                servo.trajectory[index] = trajectory[pt_index:]
            if len(servo.trajectory[0]) > 3:
                pt_table = []
                temp = list(map(list, servo.trajectory))
                for index in range(servo.DOF):
                    pt_table.append(splrep(temp[0], temp[index + 1]))
                servo.pt_table = pt_table
            servo.trajectory_lock.release()
        except ValueError:
            return self.bad
        self.last_executed_command = self.plc_time()
        servo.operative_mode = 50  # PROGRAMTRACK
        return self.good

    def _offset(self, args):
        if len(args) < 2:
            return self.bad
        servo_id = args[0]
        if servo_id not in self.servos:
            return self.bad
        servo = self.servos.get(servo_id)
        coords = args[1:]
        if len(coords) != servo.DOF:
            return self.bad
        try:
            for index, coord in enumerate(coords):
                coords[index] = float(coord)
        except ValueError:
            return self.bad
        servo.set_offsets(coords)
        self.last_executed_command = self.plc_time()
        return self.good


class Servo:

    operative_modes = {
        10: 'SETUP',
        20: 'STOW',
        30: 'STOP',
        40: 'PRESET',
        50: 'PROGRAMTRACK'
    }
    program_track_capable = False

    def __init__(self, name, dof=1):
        self.name = name
        self.enabled = 1
        self.status = 1
        self.block = 2
        self.operative_mode = 0
        self.DOF = dof
        self.coords = [random.uniform(0, 100) for _ in range(self.DOF)]
        self.offsets = [0] * self.DOF
        if self.program_track_capable:
            self.trajectory_lock = Lock()
            self.trajectory_id = None
            self.trajectory_start_time = None
            self.trajectory_point_id = None
            self.trajectory = [[] for _ in range(self.DOF + 1)]
            self.pt_table = []

    def get_status(self):
        answer = f',{self.name}_ENABLED={self.enabled}|'
        answer += f'{self.name}_STATUS={self.status}|'
        answer += f'{self.name}_BLOCK={self.block}|'
        answer += f'{self.name}_OPERATIVE_MODE={self.operative_mode}|'
        if self.operative_mode == 50:
            pt_table = []
            with self.trajectory_lock:
                pt_table = self.pt_table
            if pt_table:
                now = time.time()
                for index in range(self.DOF):
                    self.coords[index] = splev(now, pt_table[index]).item(0)
            if now > self.trajectory[0][-1]:
                with self.trajectory_lock:
                    self.trajectory_id = None
                    self.trajectory_start_time = None
                    self.trajectory_point_id = None
                    self.trajectory = [[] for _ in range(self.DOF)]
                    self.pt_table = []
        return answer

    def set_coords(self, coords):
        for index, value in enumerate(coords):
            self.coords[index] = value

    def set_offsets(self, coords):
        for index, value in enumerate(coords):
            self.offsets[index] = value


class PFP(Servo):

    def __init__(self):
        self.x_enabled = 1
        self.z_master_enabled = 1
        self.z_slave_enabled = 1
        self.theta_master_enabled = 1
        self.theta_slave_enabled = 1
        self.tx = random.uniform(0, 100)
        self.tz = random.uniform(0, 100)
        self.rtheta = random.uniform(0, 100)
        self.program_track_capable = True
        super().__init__('PFP', 3)

    def get_status(self):
        answer = super().get_status()
        answer += f'PFP_X_ENABLED={self.x_enabled}|'
        answer += f'PFP_Z_MASTER_ENABLED={self.z_master_enabled}|'
        answer += f'PFP_Z_SLAVE_ENABLED={self.z_slave_enabled}|'
        answer += f'PFP_THETA_MASTER_ENABLED={self.theta_master_enabled}|'
        answer += f'PFP_THETA_SLAVE_ENABLED={self.theta_slave_enabled}|'
        answer += f'PFP_ELONG_X={random.uniform(0, 100):.6f}|'
        answer += f'PFP_ELONG_Z_MASTER={random.uniform(0, 100):.6f}|'
        answer += f'PFP_ELONG_Z_SLAVE={random.uniform(0, 100):.6f}|'
        answer += f'PFP_ELONG_THETA_MASTER={random.uniform(0, 100):.6f}|'
        answer += f'PFP_ELONG_THETA_SLAVE={random.uniform(0, 100):.6f}|'
        answer += f'PFP_TX={self.coords[0]:.6f}|'
        answer += f'PFP_TZ={self.coords[1]:.6f}|'
        answer += f'PFP_RTHETA={self.coords[2]:.6f}|'
        answer += f'PFP_OFFSET_TX={self.offsets[0]:.6f}|'
        answer += f'PFP_OFFSET_TZ={self.offsets[1]:.6f}|'
        answer += f'PFP_OFFSET_RTHETA={self.offsets[2]:.6f}'
        return answer


class SRP(Servo):

    def __init__(self):
        self.z1_enabled = 1
        self.z2_enabled = 1
        self.z3_enabled = 1
        self.y4_enabled = 1
        self.y5_enabled = 1
        self.x6_enabled = 1
        self.tx = random.uniform(0, 100)
        self.ty = random.uniform(0, 100)
        self.tz = random.uniform(0, 100)
        self.rx = random.uniform(0, 100)
        self.ry = random.uniform(0, 100)
        self.rz = random.uniform(0, 100)
        self.program_track_capable = True
        super().__init__('SRP', 6)

    def get_status(self):
        answer = super().get_status()
        answer += f'SRP_Z1_ENABLED={self.z1_enabled}|'
        answer += f'SRP_Z2_ENABLED={self.z2_enabled}|'
        answer += f'SRP_Z3_ENABLED={self.z3_enabled}|'
        answer += f'SRP_Y1_ENABLED={self.y4_enabled}|'
        answer += f'SRP_Y2_ENABLED={self.y5_enabled}|'
        answer += f'SRP_X1_ENABLED={self.x6_enabled}|'
        answer += f'SRP_ELONG_Z1={random.uniform(0, 100):.6f}|'
        answer += f'SRP_ELONG_Z2={random.uniform(0, 100):.6f}|'
        answer += f'SRP_ELONG_Z3={random.uniform(0, 100):.6f}|'
        answer += f'SRP_ELONG_Y1={random.uniform(0, 100):.6f}|'
        answer += f'SRP_ELONG_Y2={random.uniform(0, 100):.6f}|'
        answer += f'SRP_ELONG_X1={random.uniform(0, 100):.6f}|'
        answer += f'SRP_TX={self.coords[0]:.6f}|'
        answer += f'SRP_TY={self.coords[1]:.6f}|'
        answer += f'SRP_TZ={self.coords[2]:.6f}|'
        answer += f'SRP_RX={self.coords[3]:.6f}|'
        answer += f'SRP_RY={self.coords[4]:.6f}|'
        answer += f'SRP_RZ={self.coords[5]:.6f}|'
        answer += f'SRP_OFFSET_TX={self.offsets[0]:.6f}|'
        answer += f'SRP_OFFSET_TY={self.offsets[1]:.6f}|'
        answer += f'SRP_OFFSET_TZ={self.offsets[2]:.6f}|'
        answer += f'SRP_OFFSET_RX={self.offsets[3]:.6f}|'
        answer += f'SRP_OFFSET_RY={self.offsets[4]:.6f}|'
        answer += f'SRP_OFFSET_RZ={self.offsets[5]:.6f}'
        return answer


class M3R(Servo):

    def __init__(self):
        self.cw_enabled = 1
        self.ccw_enabled = 1
        self.rotation = random.uniform(1, 100)
        super().__init__('M3R')

    def get_status(self):
        answer = super().get_status()
        answer += f'M3R_CLOCKWISE_ENABLED={self.cw_enabled}|'
        answer += f'M3R_COUNTERCLOCKWISE_ENABLED={self.ccw_enabled}|'
        answer += f'M3R_CLOCKWISE={random.uniform(0, 100):.6f}|'
        answer += f'M3R_COUNTERCLOCKWISE={random.uniform(0, 100):.6f}|'
        answer += f'M3R_ROTATION={self.coords[0]:.6f}|'
        answer += f'M3R_OFFSET={self.offsets[0]:.6f}'
        return answer


class GFR(Servo):

    def __init__(self):
        self.cw_enabled = 1
        self.ccw_enabled = 1
        self.rotation = random.uniform(1, 100)
        super().__init__('GFR')

    def get_status(self):
        answer = super().get_status()
        answer += f'GFR_CLOCKWISE_ENABLED={self.cw_enabled}|'
        answer += f'GFR_COUNTERCLOCKWISE_ENABLED={self.ccw_enabled}|'
        answer += f'GFR_CLOCKWISE={random.uniform(0, 100):.6f}|'
        answer += f'GFR_COUNTERCLOCKWISE={random.uniform(0, 100):.6f}|'
        answer += f'GFR_ROTATION={self.coords[0]:.6f}|'
        answer += f'GFR_OFFSET={self.offsets[0]:.6f}'
        return answer


class Derotator(Servo):

    def __init__(self, name):
        self.rotary_axis_enabled = 1
        self.rotation = random.uniform(1, 100)
        self.program_track_capable = True
        super().__init__(name)

    def get_status(self):
        answer = super().get_status()
        answer += f'{self.name}_ROTARY_AXIS_ENABLED='
        answer += f'{self.rotary_axis_enabled}|'
        answer += f'{self.name}_ROTATION={self.coords[0]:.6f}|'
        answer += f'{self.name}_OFFSET={self.offsets[0]:.6f}'
        return answer
