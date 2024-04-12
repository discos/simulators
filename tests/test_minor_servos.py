import unittest
import random
import time
from simulators.minor_servos import System, TIMER_VALUE


tail = '\r\n'
good = r'^OUTPUT:GOOD,[0-9]+\.[0-9]{6}'
bad = f'^OUTPUT:BAD{tail}$'


class TestMinorServos(unittest.TestCase):

    def setUp(self):
        self.system = System()

    def tearDown(self):
        del self.system

    def test_unknown_command(self):
        cmd = f'UNKNOWN{tail}'
        for byte in cmd[:-1]:
            self.assertTrue(self.system.parse(byte))
        self.assertRegex(self.system.parse(cmd[-1]), bad)

    def test_status(self):
        cmd = fr'STATUS{tail}'
        regex = good
        regex += r',CURRENT_CONFIG=0\|'
        regex += r'SIMULATION_ENABLED=1\|'
        regex += r'PLC_TIME=[0-9]+\.[0-9]+\|'
        regex += r'PLC_VERSION=1\|'
        regex += r'CONTROL=1\|'
        regex += r'POWER=1\|'
        regex += r'EMERGENCY=2\|'
        regex += r'GREGORIAN_CAP=1\|'
        regex += r'LAST_EXECUTED_COMMAND=0'
        regex += fr'{tail}$'
        for byte in cmd[:-1]:
            self.assertTrue(self.system.parse(byte))
        self.assertRegex(self.system.parse(cmd[-1]), regex)

    def test_status_unknown_servo(self):
        cmd = f'STATUS=UNKNOWN{tail}'
        for byte in cmd[:-1]:
            self.assertTrue(self.system.parse(byte))
        self.assertRegex(self.system.parse(cmd[-1]), bad)

    def test_status_PFP(self):
        cmd = fr'STATUS=PFP{tail}'
        regex = good
        regex += r',PFP_ENABLED=1\|'
        regex += r'PFP_STATUS=1\|'
        regex += r'PFP_BLOCK=2\|'
        regex += r'PFP_OPERATIVE_MODE=0\|'
        regex += r'PFP_X_ENABLED=1\|'
        regex += r'PFP_Z_MASTER_ENABLED=1\|'
        regex += r'PFP_Z_SLAVE_ENABLED=1\|'
        regex += r'PFP_THETA_MASTER_ENABLED=1\|'
        regex += r'PFP_THETA_SLAVE_ENABLED=1\|'
        regex += r'PFP_ELONG_X=[\-]?[0-9]+\.[0-9]+\|'
        regex += r'PFP_ELONG_Z_MASTER=[\-]?[0-9]+\.[0-9]+\|'
        regex += r'PFP_ELONG_Z_SLAVE=[\-]?[0-9]+\.[0-9]+\|'
        regex += r'PFP_ELONG_THETA_MASTER=[\-]?[0-9]+\.[0-9]+\|'
        regex += r'PFP_ELONG_THETA_SLAVE=[\-]?[0-9]+\.[0-9]+\|'
        regex += r'PFP_TX=[\-]?[0-9]+\.[0-9]+\|'
        regex += r'PFP_TZ=[\-]?[0-9]+\.[0-9]+\|'
        regex += r'PFP_RTHETA=[\-]?[0-9]+\.[0-9]+\|'
        regex += r'PFP_OFFSET_TX=[0-9]+\.[0-9]+\|'
        regex += r'PFP_OFFSET_TZ=[0-9]+\.[0-9]+\|'
        regex += r'PFP_OFFSET_RTHETA=[0-9]+\.[0-9]+'
        regex += fr'{tail}$'
        for byte in cmd[:-1]:
            self.assertTrue(self.system.parse(byte))
        self.assertRegex(self.system.parse(cmd[-1]), regex)

    def test_status_SRP(self):
        cmd = fr'STATUS=SRP{tail}'
        regex = good
        regex += r',SRP_ENABLED=1\|'
        regex += r'SRP_STATUS=1\|'
        regex += r'SRP_BLOCK=2\|'
        regex += r'SRP_OPERATIVE_MODE=0\|'
        regex += r'SRP_Z1_ENABLED=1\|'
        regex += r'SRP_Z2_ENABLED=1\|'
        regex += r'SRP_Z3_ENABLED=1\|'
        regex += r'SRP_Y1_ENABLED=1\|'
        regex += r'SRP_Y2_ENABLED=1\|'
        regex += r'SRP_X1_ENABLED=1\|'
        regex += r'SRP_ELONG_Z1=[\-]?[0-9]+\.[0-9]+\|'
        regex += r'SRP_ELONG_Z2=[\-]?[0-9]+\.[0-9]+\|'
        regex += r'SRP_ELONG_Z3=[\-]?[0-9]+\.[0-9]+\|'
        regex += r'SRP_ELONG_Y1=[\-]?[0-9]+\.[0-9]+\|'
        regex += r'SRP_ELONG_Y2=[\-]?[0-9]+\.[0-9]+\|'
        regex += r'SRP_ELONG_X1=[\-]?[0-9]+\.[0-9]+\|'
        regex += r'SRP_TX=[\-]?[0-9]+\.[0-9]+\|'
        regex += r'SRP_TY=[\-]?[0-9]+\.[0-9]+\|'
        regex += r'SRP_TZ=[\-]?[0-9]+\.[0-9]+\|'
        regex += r'SRP_RX=[\-]?[0-9]+\.[0-9]+\|'
        regex += r'SRP_RY=[\-]?[0-9]+\.[0-9]+\|'
        regex += r'SRP_RZ=[\-]?[0-9]+\.[0-9]+\|'
        regex += r'SRP_OFFSET_TX=[0-9]+\.[0-9]+\|'
        regex += r'SRP_OFFSET_TY=[0-9]+\.[0-9]+\|'
        regex += r'SRP_OFFSET_TZ=[0-9]+\.[0-9]+\|'
        regex += r'SRP_OFFSET_RX=[0-9]+\.[0-9]+\|'
        regex += r'SRP_OFFSET_RY=[0-9]+\.[0-9]+\|'
        regex += r'SRP_OFFSET_RZ=[0-9]+\.[0-9]+'
        regex += fr'{tail}$'
        for byte in cmd[:-1]:
            self.assertTrue(self.system.parse(byte))
        self.assertRegex(self.system.parse(cmd[-1]), regex)

    def test_status_M3R(self):
        cmd = fr'STATUS=M3R{tail}'
        regex = good
        regex += r',M3R_ENABLED=1\|'
        regex += r'M3R_STATUS=1\|'
        regex += r'M3R_BLOCK=2\|'
        regex += r'M3R_OPERATIVE_MODE=0\|'
        regex += r'M3R_CLOCKWISE_ENABLED=1\|'
        regex += r'M3R_COUNTERCLOCKWISE_ENABLED=1\|'
        regex += r'M3R_CLOCKWISE=[\-]?[0-9]+\.[0-9]+\|'
        regex += r'M3R_COUNTERCLOCKWISE=[\-]?[0-9]+\.[0-9]+\|'
        regex += r'M3R_ROTATION=[\-]?[0-9]+\.[0-9]+\|'
        regex += r'M3R_OFFSET=[0-9]+\.[0-9]+'
        regex += fr'{tail}$'
        for byte in cmd[:-1]:
            self.assertTrue(self.system.parse(byte))
        self.assertRegex(self.system.parse(cmd[-1]), regex)

    def test_status_GFR(self):
        cmd = fr'STATUS=GFR{tail}'
        regex = good
        regex += r',GFR_ENABLED=1\|'
        regex += r'GFR_STATUS=1\|'
        regex += r'GFR_BLOCK=2\|'
        regex += r'GFR_OPERATIVE_MODE=0\|'
        regex += r'GFR_CLOCKWISE_ENABLED=1\|'
        regex += r'GFR_COUNTERCLOCKWISE_ENABLED=1\|'
        regex += r'GFR_CLOCKWISE=[\-]?[0-9]+\.[0-9]+\|'
        regex += r'GFR_COUNTERCLOCKWISE=[\-]?[0-9]+\.[0-9]+\|'
        regex += r'GFR_ROTATION=[\-]?[0-9]+\.[0-9]+\|'
        regex += r'GFR_OFFSET=[0-9]+\.[0-9]+'
        regex += fr'{tail}$'
        for byte in cmd[:-1]:
            self.assertTrue(self.system.parse(byte))
        self.assertRegex(self.system.parse(cmd[-1]), regex)

    def test_status_derotators(self):
        derotators = ['GFR1', 'GFR2', 'GFR3', 'PFP']
        for derotator in derotators:
            cmd = fr'STATUS=Derotatore{derotator}{tail}'
            regex = good
            regex += fr',{derotator}_ENABLED=1\|'
            regex += fr'{derotator}_STATUS=1\|'
            regex += fr'{derotator}_BLOCK=2\|'
            regex += fr'{derotator}_OPERATIVE_MODE=0\|'
            regex += fr'{derotator}_ROTARY_AXIS_ENABLED=1\|'
            regex += fr'{derotator}_ROTATION=[\-]?[0-9]+\.[0-9]+\|'
            regex += fr'{derotator}_OFFSET=[0-9]+\.[0-9]+'
            regex += fr'{tail}$'
            for byte in cmd[:-1]:
                self.assertTrue(self.system.parse(byte))
            self.assertRegex(self.system.parse(cmd[-1]), regex)

    def test_status_too_many_args(self):
        cmd = f'STATUS=arg1,arg2{tail}'
        for byte in cmd[:-1]:
            self.assertTrue(self.system.parse(byte))
        self.assertRegex(self.system.parse(cmd[-1]), bad)

    def test_setup(self):
        configurations = self.system.configurations
        for configuration in configurations:
            cmd = f'SETUP={configuration}{tail}'
            for byte in cmd[:-1]:
                self.assertTrue(self.system.parse(byte))
            self.assertRegex(self.system.parse(cmd[-1]), f'{good}{tail}$')
            time.sleep(TIMER_VALUE + 0.1)
            for _, servo in self.system.servos.items():
                self.assertEqual(servo.operative_mode.value, 10)  # SETUP mode

    def test_setup_no_wait(self):
        cmd = f'SETUP=Gregoriano 1{tail}'
        for byte in cmd[:-1]:
            self.assertTrue(self.system.parse(byte))
        self.assertRegex(self.system.parse(cmd[-1]), f'{good}{tail}$')
        # By closing here we test that the timers get canceled

    def test_setup_no_configuration(self):
        cmd = f'SETUP{tail}'
        for byte in cmd[:-1]:
            self.assertTrue(self.system.parse(byte))
        self.assertRegex(self.system.parse(cmd[-1]), bad)

    def test_setup_unknown_configuration(self):
        cmd = f'SETUP=UNKNOWN{tail}'
        for byte in cmd[:-1]:
            self.assertTrue(self.system.parse(byte))
        self.assertRegex(self.system.parse(cmd[-1]), bad)

    def test_stow(self):
        for servo_id, servo in self.system.servos.items():
            cmd = f'STOW={servo_id},1{tail}'
            for byte in cmd[:-1]:
                self.assertTrue(self.system.parse(byte))
            self.assertRegex(self.system.parse(cmd[-1]), f'{good}{tail}$')
            time.sleep(TIMER_VALUE + 0.1)
            self.assertEqual(servo.operative_mode.value, 20)  # STOW mode

    def test_stow_gregorian_cap(self):
        for stow_pos in [1, 2]:
            cmd = f'STOW=Gregoriano,{stow_pos}{tail}'
            for byte in cmd[:-1]:
                self.assertTrue(self.system.parse(byte))
            self.assertRegex(self.system.parse(cmd[-1]), f'{good}{tail}$')
            time.sleep(TIMER_VALUE + 0.1)
            self.assertEqual(self.system.gregorian_cap.value, stow_pos)

    def test_stow_gregorian_cap_wrong_pos(self):
        cmd = f'STOW=Gregoriano,3{tail}'
        for byte in cmd[:-1]:
            self.assertTrue(self.system.parse(byte))
        self.assertRegex(self.system.parse(cmd[-1]), bad)

    def test_stow_no_arguments(self):
        cmd = f'STOW{tail}'
        for byte in cmd[:-1]:
            self.assertTrue(self.system.parse(byte))
        self.assertRegex(self.system.parse(cmd[-1]), bad)

    def test_stow_no_stow_position(self):
        for servo_id in self.system.servos:
            cmd = f'STOW={servo_id}{tail}'
            for byte in cmd[:-1]:
                self.assertTrue(self.system.parse(byte))
            self.assertRegex(self.system.parse(cmd[-1]), bad)

    def test_stow_non_integer_stow_position(self):
        for servo_id in self.system.servos:
            cmd = f'STOW={servo_id},WRONG{tail}'
            for byte in cmd[:-1]:
                self.assertTrue(self.system.parse(byte))
            self.assertRegex(self.system.parse(cmd[-1]), bad)

    def test_stow_unknown_servo(self):
        cmd = f'STOW=UNKNOWN,1{tail}'
        for byte in cmd[:-1]:
            self.assertTrue(self.system.parse(byte))
        self.assertRegex(self.system.parse(cmd[-1]), bad)

    def test_stop(self):
        for servo_id, servo in self.system.servos.items():
            cmd = f'STOP={servo_id}{tail}'
            for byte in cmd[:-1]:
                self.assertTrue(self.system.parse(byte))
            self.assertRegex(self.system.parse(cmd[-1]), f'{good}{tail}$')
            time.sleep(TIMER_VALUE + 0.1)
            self.assertEqual(servo.operative_mode.value, 30)  # STOP mode

    def test_stop_no_arguments(self):
        cmd = f'STOP{tail}'
        for byte in cmd[:-1]:
            self.assertTrue(self.system.parse(byte))
        self.assertRegex(self.system.parse(cmd[-1]), bad)

    def test_stop_unknown_servo(self):
        cmd = f'STOP=UNKNOWN{tail}'
        for byte in cmd[:-1]:
            self.assertTrue(self.system.parse(byte))
        self.assertRegex(self.system.parse(cmd[-1]), bad)

    def test_preset(self):
        for servo_id, servo in self.system.servos.items():
            DOF = servo.DOF
            coords = [random.uniform(0, 100) for _ in range(DOF)]
            cmd = f'PRESET={servo_id},{",".join(map(str, coords))}{tail}'
            for byte in cmd[:-1]:
                self.assertTrue(self.system.parse(byte))
            self.assertRegex(self.system.parse(cmd[-1]), f'{good}{tail}$')
            time.sleep(TIMER_VALUE + 0.1)
            self.assertEqual(coords, servo.coords)
            self.assertEqual(servo.operative_mode.value, 40)  # PRESET mode

    def test_preset_no_arguments(self):
        cmd = f'PRESET{tail}'
        for byte in cmd[:-1]:
            self.assertTrue(self.system.parse(byte))
        self.assertRegex(self.system.parse(cmd[-1]), bad)

    def test_preset_too_many_args(self):
        for servo, _ in self.system.servos.items():
            DOF = 10  # WAY TOO MANY COORDINATES
            coords = [random.uniform(0, 100) for _ in range(DOF)]
            cmd = f'PRESET={servo},{",".join(map(str, coords))}{tail}'
            for byte in cmd[:-1]:
                self.assertTrue(self.system.parse(byte))
            self.assertRegex(self.system.parse(cmd[-1]), bad)

    def test_preset_unknown_servo(self):
        cmd = f'PRESET=UNKNOWN,1{tail}'
        for byte in cmd[:-1]:
            self.assertTrue(self.system.parse(byte))
        self.assertRegex(self.system.parse(cmd[-1]), bad)

    def test_preset_non_numeric_coordinates(self):
        for servo_id, servo in self.system.servos.items():
            DOF = servo.DOF
            coords = ['STRING' for _ in range(DOF)]
            cmd = f'PRESET={servo_id},{",".join(map(str, coords))}{tail}'
            for byte in cmd[:-1]:
                self.assertTrue(self.system.parse(byte))
            self.assertRegex(self.system.parse(cmd[-1]), bad)

    def test_program_track(self):
        start_time = time.time() + 0.05
        for servo_id, servo in self.system.servos.items():
            coords = [random.uniform(0, 100) for _ in range(servo.DOF)]
            cmd = f'PROGRAMTRACK={servo_id},0,0,{start_time:.6f},'
            cmd += f'{",".join(map(str, coords))}{tail}'
            for byte in cmd[:-1]:
                self.assertTrue(self.system.parse(byte))
            if servo.program_track_capable:
                self.assertRegex(self.system.parse(cmd[-1]), f'{good}{tail}$')
                self.assertEqual(servo.operative_mode.value, 50)
                # PROGRAMTRACK mode
            else:
                self.assertRegex(self.system.parse(cmd[-1]), bad)

    def test_program_track_wrong_start_time_format(self):
        for servo_id, servo in self.system.servos.items():
            coords = [random.uniform(0, 100) for _ in range(servo.DOF)]
            cmd = f'PROGRAMTRACK={servo_id},0,0,START_TIME,'
            cmd += f'{",".join(map(str, coords))}{tail}'
            for byte in cmd[:-1]:
                self.assertTrue(self.system.parse(byte))
            self.assertRegex(self.system.parse(cmd[-1]), bad)

    def test_program_track_spline(self):
        start_time = time.time() + 3
        for servo_id, servo in self.system.servos.items():
            for point_id in range(10):
                cmd = f'PROGRAMTRACK={servo_id},0,{point_id},'
                if point_id == 0:
                    cmd += f'{start_time:.6f},'
                    coords = [0.0 for _ in range(servo.DOF)]
                else:
                    cmd += '*,'
                    coords = [random.uniform(0, 100) for _ in range(servo.DOF)]
                cmd += f'{",".join(map(str, coords))}{tail}'
                for byte in cmd[:-1]:
                    self.assertTrue(self.system.parse(byte))
                if servo.program_track_capable:
                    self.assertRegex(
                        self.system.parse(cmd[-1]),
                        f'{good}{tail}$'
                    )
                    self.assertEqual(servo.operative_mode.value, 50)
                    # PROGRAMTRACK mode
                else:
                    self.assertRegex(self.system.parse(cmd[-1]), bad)
        # Check if the trajectory is being tracked
        for servo_id, servo in self.system.servos.items():
            if servo.program_track_capable:
                servo.get_status(start_time + 0.5)
                for index in range(servo.DOF):
                    self.assertNotEqual(servo.coords[index], 0)
        # Check if the trajectory has been completed
        for servo_id, servo in self.system.servos.items():
            if servo.program_track_capable:
                servo.get_status(start_time + 10)
                self.assertEqual(servo.pt_table, [])

    def test_program_track_start_with_wrong_point_id(self):
        start_time = time.time() + 3
        for servo_id, servo in self.system.servos.items():
            coords = [random.uniform(0, 100) for _ in range(servo.DOF)]
            cmd = f'PROGRAMTRACK={servo_id},0,10,{start_time:.6f},'
            cmd += f'{",".join(map(str, coords))}{tail}'
            for byte in cmd[:-1]:
                self.assertTrue(self.system.parse(byte))
            self.assertRegex(self.system.parse(cmd[-1]), bad)

    def test_program_track_start_way_in_the_future(self):
        start_time = time.time() * 1000000
        for servo_id, servo in self.system.servos.items():
            coords = [random.uniform(0, 100) for _ in range(servo.DOF)]
            cmd = f'PROGRAMTRACK={servo_id},0,0,{start_time:.6f},'
            cmd += f'{",".join(map(str, coords))}{tail}'
            for byte in cmd[:-1]:
                self.assertTrue(self.system.parse(byte))
            if servo.program_track_capable:
                self.assertRegex(self.system.parse(cmd[-1]), f'{good}{tail}$')
            else:
                self.assertRegex(self.system.parse(cmd[-1]), bad)

    def test_program_track_append_with_start(self):
        self.test_program_track()
        for servo_id, servo in self.system.servos.items():
            DOF = servo.DOF
            coords = [random.uniform(0, 100) for _ in range(DOF)]
            cmd = f'PROGRAMTRACK={servo_id},0,1,*,'
            cmd += f'{",".join(map(str, coords))}{tail}'
            for byte in cmd[:-1]:
                self.assertTrue(self.system.parse(byte))
            if servo.program_track_capable:
                self.assertRegex(self.system.parse(cmd[-1]), f'{good}{tail}$')
                self.assertEqual(servo.operative_mode.value, 50)
                # PROGRAMTRACK mode
            else:
                self.assertRegex(self.system.parse(cmd[-1]), bad)

    def test_program_track_append_without_start(self):
        for servo_id, servo in self.system.servos.items():
            DOF = servo.DOF
            coords = [random.uniform(0, 100) for _ in range(DOF)]
            cmd = f'PROGRAMTRACK={servo_id},0,0,*,'
            cmd += f'{",".join(map(str, coords))}{tail}'
            for byte in cmd[:-1]:
                self.assertTrue(self.system.parse(byte))
            self.assertRegex(self.system.parse(cmd[-1]), bad)

    def test_program_track_append_with_wrong_point_id(self):
        self.test_program_track()
        for servo_id, servo in self.system.servos.items():
            DOF = servo.DOF
            coords = [random.uniform(0, 100) for _ in range(DOF)]
            cmd = f'PROGRAMTRACK={servo_id},0,10,*,'
            cmd += f'{",".join(map(str, coords))}{tail}'
            for byte in cmd[:-1]:
                self.assertTrue(self.system.parse(byte))
            self.assertRegex(self.system.parse(cmd[-1]), bad)

    def test_program_track_append_too_late(self):
        self.test_program_track()
        time.sleep(0.3)
        for servo_id, servo in self.system.servos.items():
            DOF = servo.DOF
            coords = [random.uniform(0, 100) for _ in range(DOF)]
            cmd = f'PROGRAMTRACK={servo_id},0,1,*,'
            cmd += f'{",".join(map(str, coords))}{tail}'
            for byte in cmd[:-1]:
                self.assertTrue(self.system.parse(byte))
            self.assertRegex(self.system.parse(cmd[-1]), bad)

    def test_program_track_old_start_time(self):
        start_time = time.time() - 3
        for servo_id, servo in self.system.servos.items():
            DOF = servo.DOF
            coords = [random.uniform(0, 100) for _ in range(DOF)]
            cmd = f'PROGRAMTRACK={servo_id},0,0,{start_time:.6f},'
            cmd += f'{",".join(map(str, coords))}{tail}'
            for byte in cmd[:-1]:
                self.assertTrue(self.system.parse(byte))
            self.assertRegex(self.system.parse(cmd[-1]), bad)

    def test_program_track_old_point_id(self):
        self.test_program_track()
        for servo_id, servo in self.system.servos.items():
            DOF = servo.DOF
            coords = [random.uniform(0, 100) for _ in range(DOF)]
            cmd = f'PROGRAMTRACK={servo_id},0,-10,*,'
            cmd += f'{",".join(map(str, coords))}{tail}'
            for byte in cmd[:-1]:
                self.assertTrue(self.system.parse(byte))
            self.assertRegex(self.system.parse(cmd[-1]), bad)

    def test_program_track_no_arguments(self):
        cmd = f'PROGRAMTRACK{tail}'
        for byte in cmd[:-1]:
            self.assertTrue(self.system.parse(byte))
        self.assertRegex(self.system.parse(cmd[-1]), bad)

    def test_program_track_too_many_arguments(self):
        start_time = time.time() + 3
        for servo_id in self.system.servos:
            DOF = 10  # Too many coordinates
            coords = [random.uniform(0, 100) for _ in range(DOF)]
            cmd = f'PROGRAMTRACK={servo_id},0,0,{start_time:.6f},'
            cmd += f'{",".join(map(str, coords))}{tail}'
            for byte in cmd[:-1]:
                self.assertTrue(self.system.parse(byte))
            self.assertRegex(self.system.parse(cmd[-1]), bad)

    def test_program_track_unknown_servo(self):
        start_time = time.time() + 3
        cmd = f'PROGRAMTRACK=UNKNOWN,0,0,{start_time:.6f},0{tail}'
        for byte in cmd[:-1]:
            self.assertTrue(self.system.parse(byte))
        self.assertRegex(self.system.parse(cmd[-1]), bad)

    def test_program_track_non_numeric_trajectory_id(self):
        start_time = time.time() + 3
        for servo_id, servo in self.system.servos.items():
            DOF = servo.DOF
            coords = [random.uniform(0, 100) for _ in range(DOF)]
            cmd = f'PROGRAMTRACK={servo_id},NAN,0,{start_time:.6f},'
            cmd += f'{",".join(map(str, coords))}{tail}'
            for byte in cmd[:-1]:
                self.assertTrue(self.system.parse(byte))
            self.assertRegex(self.system.parse(cmd[-1]), bad)

    def test_offset(self):
        for servo_id, servo in self.system.servos.items():
            DOF = servo.DOF
            coords = [random.uniform(0, 100) for _ in range(DOF)]
            cmd = f'OFFSET={servo_id},{",".join(map(str, coords))}{tail}'
            for byte in cmd[:-1]:
                self.assertTrue(self.system.parse(byte))
            self.assertRegex(self.system.parse(cmd[-1]), f'{good}{tail}$')
            self.assertEqual(coords, servo.offsets)

    def test_offset_no_arguments(self):
        cmd = f'OFFSET{tail}'
        for byte in cmd[:-1]:
            self.assertTrue(self.system.parse(byte))
        self.assertRegex(self.system.parse(cmd[-1]), bad)

    def test_offset_too_many_args(self):
        for servo_id in self.system.servos:
            DOF = 10  # WAY TOO MANY COORDINATES
            coords = [random.uniform(0, 100) for _ in range(DOF)]
            cmd = f'OFFSET={servo_id},{",".join(map(str, coords))}{tail}'
            for byte in cmd[:-1]:
                self.assertTrue(self.system.parse(byte))
            self.assertRegex(self.system.parse(cmd[-1]), bad)

    def test_offset_unknown_servo(self):
        cmd = f'OFFSET=UNKNOWN,1{tail}'
        for byte in cmd[:-1]:
            self.assertTrue(self.system.parse(byte))
        self.assertRegex(self.system.parse(cmd[-1]), bad)

    def test_offset_non_numeric_coordinates(self):
        for servo_id, servo in self.system.servos.items():
            DOF = servo.DOF
            coords = ['STRING' for _ in range(DOF)]
            cmd = f'OFFSET={servo_id},{",".join(map(str, coords))}{tail}'
            for byte in cmd[:-1]:
                self.assertTrue(self.system.parse(byte))
            self.assertRegex(self.system.parse(cmd[-1]), bad)


if __name__ == '__main__':
    unittest.main()
