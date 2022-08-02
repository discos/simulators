import unittest
import random
from simulators import gaia


class TestGaia(unittest.TestCase):

    def setUp(self):
        self.system = gaia.System()
        self.id = random.randint(0, 1023)

    def wrap(self, raw_response):
        return '#%s %s\n' % (raw_response, self.id)

    def test_idn(self):
        expected_answer = self.wrap('GAIA Simulator Rev. 1.0.0 / 2022.02.08.1')
        command = self.wrap('*IDN?')
        for byte in command[:-1]:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.parse(command[-1]), expected_answer)

    def test_conf(self):
        conf = 5
        expected_answer = self.wrap(5)
        command = self.wrap('LOADCONF %s' % conf)
        for byte in command[:-1]:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.parse(command[-1]), expected_answer)
        # Get the configuration
        command = self.wrap('CONF?')
        for byte in command[:-1]:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.parse(command[-1]), expected_answer)

    def test_setd(self):
        expected_answer = self.wrap(1)
        command = self.wrap('SETD 1 0')
        for byte in command[:-1]:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.parse(command[-1]), expected_answer)

    def test_setg(self):
        expected_answer = self.wrap(1)
        command = self.wrap('SETG 1 0')
        for byte in command[:-1]:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.parse(command[-1]), expected_answer)

    def test_setsg(self):
        expected_answer = self.wrap(1)
        command = self.wrap('SETSG 1')
        for byte in command[:-1]:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.parse(command[-1]), expected_answer)

    def test_setsd(self):
        expected_answer = self.wrap(1)
        command = self.wrap('SETSD 1')
        for byte in command[:-1]:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.parse(command[-1]), expected_answer)

    def test_setsgz(self):
        expected_answer = self.wrap(1)
        command = self.wrap('SETSGZ 1')
        for byte in command[:-1]:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.parse(command[-1]), expected_answer)

    def test_setsdz(self):
        expected_answer = self.wrap(1)
        command = self.wrap('SETSDZ 1')
        for byte in command[:-1]:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.parse(command[-1]), expected_answer)

    def test_savecpu(self):
        expected_answer = self.wrap('1')
        command = self.wrap('SAVECPU 1')
        for byte in command[:-1]:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.parse(command[-1]), expected_answer)

    def test_resetd(self):
        expected_answer = self.wrap(1)
        command = self.wrap('RESETD 1')
        for byte in command[:-1]:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.parse(command[-1]), expected_answer)

    def test_resetg(self):
        expected_answer = self.wrap(1)
        command = self.wrap('RESETG 1')
        for byte in command[:-1]:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.parse(command[-1]), expected_answer)

    def test_save(self):
        expected_answer = self.wrap(1)
        command = self.wrap('SAVE 1')
        for byte in command[:-1]:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.parse(command[-1]), expected_answer)

    def test_setdf(self):
        expected_answer = self.wrap(1)
        command = self.wrap('SETDF 1')
        for byte in command[:-1]:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.parse(command[-1]), expected_answer)

    def test_setgf(self):
        expected_answer = self.wrap(1)
        command = self.wrap('SETGF 1')
        for byte in command[:-1]:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.parse(command[-1]), expected_answer)

    def test_getef(self):
        expected_answer = self.wrap(1)
        command = self.wrap('GETEF 1')
        for byte in command[:-1]:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.parse(command[-1]), expected_answer)

    def test_enable(self):
        expected_answer = self.wrap(1)
        command = self.wrap('ENABLE 1')
        for byte in command[:-1]:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.parse(command[-1]), expected_answer)

    def test_disable(self):
        expected_answer = self.wrap(1)
        command = self.wrap('DISABLE 1')
        for byte in command[:-1]:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.parse(command[-1]), expected_answer)

    def test_getvg(self):
        expected_answer = self.wrap(0)
        command = self.wrap('GETVG 1')
        for byte in command[:-1]:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.parse(command[-1]), expected_answer)

    def test_getvd(self):
        expected_answer = self.wrap(0)
        command = self.wrap('GETVD 1')
        for byte in command[:-1]:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.parse(command[-1]), expected_answer)

    def test_getid(self):
        expected_answer = self.wrap(0)
        command = self.wrap('GETID 1')
        for byte in command[:-1]:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.parse(command[-1]), expected_answer)

    def test_getref(self):
        expected_answer = self.wrap('2.5')
        command = self.wrap('GETREF 1')
        for byte in command[:-1]:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.parse(command[-1]), expected_answer)
        expected_answer = self.wrap(5)
        command = self.wrap('GETREF 2')
        for byte in command[:-1]:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.parse(command[-1]), expected_answer)

    def test_getemp(self):
        command = self.wrap('GETEMP 1')
        for byte in command[:-1]:
            self.assertTrue(self.system.parse(byte))
        answer = self.system.parse(command[-1])
        temperature = answer.lstrip('#').split()[-2]
        self.assertIn(int(temperature), range(30, 37))

    def test_name(self):
        expected_answer = self.wrap('GAIASIMBOARD')
        command = self.wrap('NAME?')
        for byte in command[:-1]:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.parse(command[-1]), expected_answer)

    def test_args_not_valid(self):
        command = '#\n'
        for byte in command[:-1]:
            self.assertTrue(self.system.parse(byte))
        answer = self.system.parse(command[-1])
        self.assertIn('ERROR(1000)[ERROR_ARGS_NOT_VALID]', answer)

    def test_no_args(self):
        command = '#SETD\n'
        for byte in command[:-1]:
            self.assertTrue(self.system.parse(byte))
        answer = self.system.parse(command[-1])
        self.assertIn('ERROR(1004)[ERROR_NO_ARGS]', answer)

    def test_unknown_command(self):
        command = self.wrap('UNKNOWN')
        for byte in command[:-1]:
            self.assertTrue(self.system.parse(byte))
        answer = self.system.parse(command[-1])
        self.assertIn('ERROR(1001)[ERROR_COMMAND_UNKNOWN]', answer)

    def test_too_many_args(self):
        command = self.wrap('SETD 1 1 1')
        for byte in command[:-1]:
            self.assertTrue(self.system.parse(byte))
        answer = self.system.parse(command[-1])
        self.assertIn('ERROR(1015)[ERROR_TOO_MANY_ARGS]', answer)

    def test_first_arg_not_integer(self):
        command = self.wrap('GETEMP A')
        for byte in command[:-1]:
            self.assertTrue(self.system.parse(byte))
        answer = self.system.parse(command[-1])
        self.assertIn('ERROR(1002)[ERROR_FIRST_ARG_NOT_NUMBER]', answer)

    def test_first_arg_out_of_range(self):
        command = self.wrap('GETEMP 100')
        for byte in command[:-1]:
            self.assertTrue(self.system.parse(byte))
        answer = self.system.parse(command[-1])
        self.assertIn('ERROR(1003)[ERROR_FIRST_ARG_OUT_OF_RANGE]', answer)

    def test_second_arg_missing(self):
        command = self.wrap('SETD 1')
        for byte in command[:-1]:
            self.assertTrue(self.system.parse(byte))
        answer = self.system.parse(command[-1])
        self.assertIn('ERROR(1008)[ERROR_SECOND_ARG_NOT_PRESENT]', answer)

    def test_second_arg_not_integer(self):
        command = self.wrap('SETD 1 A')
        for byte in command[:-1]:
            self.assertTrue(self.system.parse(byte))
        answer = self.system.parse(command[-1])
        self.assertIn('ERROR(1009)[ERROR_SECOND_ARG_NOT_NUMBER]', answer)

    def test_second_arg_out_of_range(self):
        command = self.wrap('SETD 1 5000')
        for byte in command[:-1]:
            self.assertTrue(self.system.parse(byte))
        answer = self.system.parse(command[-1])
        self.assertIn('ERROR(1010)[ERROR_SECOND_ARG_OUT_OF_RANGE]', answer)

    def test_no_header(self):
        command = 'noheader'
        for byte in command[:-1]:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.msg, '')


if __name__ == '__main__':
    unittest.main()
