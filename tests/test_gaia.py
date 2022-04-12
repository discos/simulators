import unittest
from simulators import gaia


class TestGaia(unittest.TestCase):

    def setUp(self):
        self.system = gaia.System()

    def test_idn(self):
        expected_answer = 'GAIA Simulator Rev. 1.0.0 / 2022.02.08.1\n'
        command = '#*IDN?\n'
        for byte in command[:-1]:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.parse(command[-1]), expected_answer)
        command = '*IDN?\n'
        for byte in command[:-1]:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.parse(command[-1]), expected_answer)

    def test_setd(self):
        expected_answer = '1\n'
        command = '#SETD 1 0\n'
        for byte in command[:-1]:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.parse(command[-1]), expected_answer)

    def test_setg(self):
        expected_answer = '1\n'
        command = '#SETG 1 0\n'
        for byte in command[:-1]:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.parse(command[-1]), expected_answer)

    def test_setsg(self):
        expected_answer = '1\n'
        command = '#SETSG 1\n'
        for byte in command[:-1]:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.parse(command[-1]), expected_answer)

    def test_setsd(self):
        expected_answer = '1\n'
        command = '#SETSD 1\n'
        for byte in command[:-1]:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.parse(command[-1]), expected_answer)

    def test_setsgz(self):
        expected_answer = '1\n'
        command = '#SETSGZ 1\n'
        for byte in command[:-1]:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.parse(command[-1]), expected_answer)

    def test_setsdz(self):
        expected_answer = '1\n'
        command = '#SETSDZ 1\n'
        for byte in command[:-1]:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.parse(command[-1]), expected_answer)

    def test_savecpu(self):
        expected_answer = '1\n'
        command = '#SAVECPU 1\n'
        for byte in command[:-1]:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.parse(command[-1]), expected_answer)

    def test_resetd(self):
        expected_answer = '1\n'
        command = '#RESETD 1\n'
        for byte in command[:-1]:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.parse(command[-1]), expected_answer)

    def test_resetg(self):
        expected_answer = '1\n'
        command = '#RESETG 1\n'
        for byte in command[:-1]:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.parse(command[-1]), expected_answer)

    def test_save(self):
        expected_answer = '1\n'
        command = '#SAVE 1\n'
        for byte in command[:-1]:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.parse(command[-1]), expected_answer)

    def test_setdf(self):
        expected_answer = '1\n'
        command = '#SETDF 1\n'
        for byte in command[:-1]:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.parse(command[-1]), expected_answer)

    def test_setgf(self):
        expected_answer = '1\n'
        command = '#SETGF 1\n'
        for byte in command[:-1]:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.parse(command[-1]), expected_answer)

    def test_getef(self):
        expected_answer = '1\n'
        command = '#GETEF 1\n'
        for byte in command[:-1]:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.parse(command[-1]), expected_answer)

    def test_enable(self):
        expected_answer = '1\n'
        command = '#ENABLE 1\n'
        for byte in command[:-1]:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.parse(command[-1]), expected_answer)

    def test_disable(self):
        expected_answer = '1\n'
        command = '#DISABLE 1\n'
        for byte in command[:-1]:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.parse(command[-1]), expected_answer)

    def test_getvg(self):
        expected_answer = '0\n'
        command = '#GETVG 1\n'
        for byte in command[:-1]:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.parse(command[-1]), expected_answer)

    def test_getvd(self):
        expected_answer = '0\n'
        command = '#GETVD 1\n'
        for byte in command[:-1]:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.parse(command[-1]), expected_answer)

    def test_getid(self):
        expected_answer = '0\n'
        command = '#GETID 1\n'
        for byte in command[:-1]:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.parse(command[-1]), expected_answer)

    def test_getref(self):
        expected_answer = '2.5\n'
        command = '#GETREF 1\n'
        for byte in command[:-1]:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.parse(command[-1]), expected_answer)
        expected_answer = '5\n'
        command = '#GETREF 2\n'
        for byte in command[:-1]:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.parse(command[-1]), expected_answer)

    def test_getemp(self):
        command = '#GETEMP 1\n'
        for byte in command[:-1]:
            self.assertTrue(self.system.parse(byte))
        answer = int(self.system.parse(command[-1]))
        self.assertIn(answer, range(30, 37))

    def test_name(self):
        expected_answer = 'GAIASIMBOARD\n'
        command = '#NAME?\n'
        for byte in command[:-1]:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.parse(command[-1]), expected_answer)

    def test_args_not_valid(self):
        expected_answer = (
            'ERROR(1000)[ERROR_ARGS_NOT_VALID]'
            '(4552524f525f415247535f4e4f545f56414c4944)\n'
        )
        command = '\n'
        for byte in command[:-1]:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.parse(command[-1]), expected_answer)

    def test_no_args(self):
        expected_answer = (
            'ERROR(1004)[ERROR_NO_ARGS]'
            '(4552524f525f4e4f5f41524753)\n'
        )
        command = '#SETD\n'
        for byte in command[:-1]:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.parse(command[-1]), expected_answer)

    def test_unknown_command(self):
        expected_answer = (
            'ERROR(1001)[ERROR_COMMAND_UNKNOWN]'
            '(4552524f525f434f4d4d414e445f554e4b4e4f574e)\n'
        )
        command = '#UNKNOWN\n'
        for byte in command[:-1]:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.parse(command[-1]), expected_answer)

    def test_too_many_args(self):
        expected_answer = (
            'ERROR(1015)[ERROR_TOO_MANY_ARGS]'
            '(4552524f525f544f4f5f4d414e595f41524753)\n'
        )
        command = '#SETD 1 1 1\n'
        for byte in command[:-1]:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.parse(command[-1]), expected_answer)

    def test_first_arg_not_integer(self):
        expected_answer = (
            'ERROR(1002)[ERROR_FIRST_ARG_NOT_NUMBER]'
            '(4552524f525f46495253545f4152475f4e4f545f4e554d424552)\n'
        )
        command = '#GETEMP A\n'
        for byte in command[:-1]:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.parse(command[-1]), expected_answer)

    def test_first_arg_out_of_range(self):
        expected_answer = (
            'ERROR(1003)[ERROR_FIRST_ARG_OUT_OF_RANGE]'
            '(4552524f525f46495253545f4152475f4f55545f4f465f52414e4745)\n'
        )
        command = '#GETEMP 100\n'
        for byte in command[:-1]:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.parse(command[-1]), expected_answer)

    def test_second_arg_missing(self):
        expected_answer = (
            'ERROR(1008)[ERROR_SECOND_ARG_NOT_PRESENT]'
            '(4552524f525f5345434f4e445f4152475f4e4f545f50524553454e54)\n'
        )
        command = '#SETD 1\n'
        for byte in command[:-1]:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.parse(command[-1]), expected_answer)

    def test_second_arg_not_integer(self):
        expected_answer = (
            'ERROR(1009)[ERROR_SECOND_ARG_NOT_NUMBER]'
            '(4552524f525f5345434f4e445f4152475f4e4f545f4e554d424552)\n'
        )
        command = '#SETD 1 A\n'
        for byte in command[:-1]:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.parse(command[-1]), expected_answer)

    def test_second_arg_out_of_range(self):
        expected_answer = (
            'ERROR(1010)[ERROR_SECOND_ARG_OUT_OF_RANGE]'
            '(4552524f525f5345434f4e445f4152475f4f55545f4f465f52414e4745)\n'
        )
        command = '#SETD 1 5000\n'
        for byte in command[:-1]:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.parse(command[-1]), expected_answer)


if __name__ == '__main__':
    unittest.main()
