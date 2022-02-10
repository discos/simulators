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


if __name__ == '__main__':
    unittest.main()
