import unittest
from simulators import dbesm


class TestDBESM(unittest.TestCase):

    def setUp(self):
        self.system = dbesm.System()

    def _send(self, message):
        for byte in message[:-1]:
            self.assertTrue(self.system.parse(byte))
        response = self.system.parse(message[-1])
        return response

    def _disable_board(self, err_board=3):
        disable_msg = f'DBE SETSTATUS BOARD {err_board} VALUE 1\x0D\x0A'
        self._send(disable_msg)

    def _noTemp_board(self, err_board=3):
        noTemp_msg = f'DBE SETSTATUS BOARD {err_board} VALUE 2\x0D\x0A'
        self._send(noTemp_msg)

    def _test_all_boards(self, response, err_board=999, diag=False):
        for board in range(1, 5):
            if diag:
                if board != err_board:
                    self.assertRegex(response, f'BOARD {board} ACK\n5V '
                    '[0-9][.][0-9]+ 3V3 [0-9][.][0-9]+\nT0 [0-9]+[.][0-9]+')
                else:
                    self.assertRegex(response, f'BOARD {board} ERR DBE '
                    'BOARD unreachable')
            else:
                if board != err_board:
                    self.assertRegex(response, f'BOARD {board} ACK')
                else:
                    self.assertRegex(response, f'BOARD {board} ERR DBE '
                    'BOARD unreachable')

#       NAK generic

    def test_nak_generic(self):
        message = "?????\x0D\x0A"
        response = self._send(message)
        self.assertEqual(response, 'NAK unknown command\x0D\x0A')

    def test_nak_dbe_generic(self):
        message = "DBE ?????\x0D\x0A"
        response = self._send(message)
        self.assertEqual(response, 'NAK unknown command\x0D\x0A')

    def test_nak_dbe(self):
        message = "DBE\x0D\x0A"
        response = self._send(message)
        self.assertEqual(response, 'NAK unknown command\x0D\x0A')

    def test_nak_all_2spaces(self):
        message = "DBE SETALLMODE  MFS_7\x0D\x0A"
        response = self._send(message)
        self.assertEqual(response, 'NAK unknown command\x0D\x0A')

    def test_nak_set_2spaces(self, ch=0, board=1, val=0.0):
        message = f"DBE SETATT  {ch} BOARD {board} VALUE {val}\x0D\x0A"
        response = self._send(message)
        self.assertEqual(response, 'NAK unknown command\x0D\x0A')

    def test_nak_set_3spaces(self, ch=0, board=1, val=0.0):
        message = f"DBE SETATT   {ch} BOARD {board} VALUE {val}\x0D\x0A"
        response = self._send(message)
        self.assertEqual(response, 'NAK unknown command\x0D\x0A')

    def test_nak_set_space_end(self, ch=0, board=1, val=0.0):
        message = f"DBE SETATT {ch} BOARD {board} VALUE {val} \x0D\x0A"
        response = self._send(message)
        self.assertEqual(response, 'NAK unknown command\x0D\x0A')

    def test_nak_set_2spaces_end(self, ch=0, board=1, val=0.0):
        message = f"DBE SETATT {ch} BOARD {board} VALUE {val}  \x0D\x0A"
        response = self._send(message)
        self.assertEqual(response, 'NAK unknown command\x0D\x0A')

    def test_nak_set_3spaces_end(self, ch=0, board=1, val=0.0):
        message = f"DBE SETATT {ch} BOARD {board} VALUE {val}   \x0D\x0A"
        response = self._send(message)
        self.assertEqual(response, 'NAK unknown command\x0D\x0A')

    def test_nak_mispell1(self, ch=0, board=1, val=0.0):
        message = f"DBE SETATT {ch} OARD {board} VALUE {val}\x0D\x0A"
        response = self._send(message)
        self.assertEqual(response, 'NAK unknown command\x0D\x0A')

    def test_nak_mispell2(self, ch=0, board=1, val=0.0):
        message = f"DBE SETATT {ch} BOARD {board} VALE {val}\x0D\x0A"
        response = self._send(message)
        self.assertEqual(response, 'NAK unknown command\x0D\x0A')

#       SETSTATUS

    def test_setstatus_ok(self, board=2, val=1):
        message = f"DBE SETSTATUS BOARD {board} VALUE {val}\x0D\x0A"
        response = self._send(message)
        self.assertEqual(response, 'ACK\x0D\x0A')

    def test_setstatus_noBoard(self, board=999, val=1):
        message = f"DBE SETSTATUS BOARD {board} VALUE {val}\x0D\x0A"
        response = self._send(message)
        self.assertEqual(response, f'ERR DBE BOARD {board} '
        'not existing\x0D\x0A')

    def test_nak_setstatus_missing(self, board=1):
        message = f"DBE SETSTATUS BOARD {board} VALUE\x0D\x0A"
        response = self._send(message)
        self.assertEqual(response, 'NAK unknown command\x0D\x0A')

    def test_nak_setstaus_notIntBoard(self, board='BOARD', val=1):
        message = f"DBE SETSTATUS BOARD {board} VALUE {val}\x0D\x0A"
        response = self._send(message)
        self.assertEqual(response, 'NAK unknown command\x0D\x0A')

    def test_nak_setstaus_notIntVal(self, board=1, val='VALUE'):
        message = f"DBE SETSTATUS BOARD {board} VALUE {val}\x0D\x0A"
        response = self._send(message)
        self.assertEqual(response, 'NAK unknown command\x0D\x0A')

#       ReadALLDIAG, DELETEFILE

    def test_all_diag_ok(self):
        message = "DBE ReadALLDIAG\x0D\x0A"
        response = self._send(message)
        # self.assertEqual(len(response), 1)
        # self.assertEqual(response[0], 'ack')
        self._test_all_boards(response)

    def test_all_diag_boardErr(self, err_board=3):
        message = "DBE ReadALLDIAG\x0D\x0A"
        self._disable_board(err_board)
        response = self._send(message)
        self._test_all_boards(response, err_board, True)

    def test_all_diag_noTemp(self, err_board=3):
        message = "DBE ReadALLDIAG\x0D\x0A"
        self._noTemp_board(err_board)
        response = self._send(message)
        for board in range(1, 5):
            if board != err_board:
                self.assertRegex(response, f'BOARD {board} ACK\n5V '
                '[0-9][.][0-9]+ 3V3 [0-9][.][0-9]+\nT0 [0-9]+[.][0-9]+')
            else:
                self.assertRegex(response, f'BOARD {board} ACK\n5V '
                '[0-9][.][0-9]+ 3V3 [0-9][.][0-9]+\ntemp sensor not present')

    def test_nak_alldiag(self):
        message = "DBE ReadALLDIAG ?????\x0D\x0A"
        response = self._send(message)
        self.assertEqual(response, 'NAK unknown command\x0D\x0A')

    def test_deletefile_ok(self, obs_mode='CustomCfg'):
        message1 = f"DBE STOREALLMODE {obs_mode}\x0D\x0A"
        self._send(message1)
        message = f"DBE DELETEFILE {obs_mode}\x0D\x0A"
        response = self._send(message)
        self.assertEqual(response, 'ACK\x0D\x0A')

    def test_deletefile_err(self, obs_mode='CustomCfg'):
        message = f"DBE DELETEFILE {obs_mode}\x0D\x0A"
        response = self._send(message)
        self.assertEqual(response, 'ERR DBE CFG file not existing\x0D\x0A')

    def test_nak_deletefile_missing(self):
        message = "DBE DELETEFILE\x0D\x0A"
        response = self._send(message)
        self.assertEqual(response, 'NAK unknown command\x0D\x0A')

#       SETALLMODE, STOREALLMODE

    def test_setallmode_ok(self, obs_mode='MFS_7'):
        message = f"DBE SETALLMODE {obs_mode}\x0D\x0A"
        response = self._send(message)
        self._test_all_boards(response)

    def test_setallmode_boardErr(self, obs_mode='MFS_7', err_board=3):
        message = f"DBE SETALLMODE {obs_mode}\x0D\x0A"
        self._disable_board(err_board)
        response = self._send(message)
        self._test_all_boards(response, err_board)

    def test_setallmode_cfgErr(self, obs_mode='PIPPO'):
        message = f"DBE SETALLMODE {obs_mode}\x0D\x0A"
        response = self._send(message)
        self.assertEqual(response, 'ERR DBE CFG file not existing\x0D\x0A')

    def test_setallmode_bothErr(self, obs_mode='PIPPO', err_board=3):
        message = f"DBE SETALLMODE {obs_mode}\x0D\x0A"
        self._disable_board(err_board)
        response = self._send(message)
        self.assertEqual(response, 'ERR DBE CFG file not existing\x0D\x0A')

    def test_nak_setall_missing(self):
        message = "DBE SETALLMODE\x0D\x0A"
        response = self._send(message)
        self.assertEqual(response, 'NAK unknown command\x0D\x0A')

    def test_storeallmode_ok(self, obs_mode='CustomCfg'):
        message = f"DBE STOREALLMODE {obs_mode}\x0D\x0A"
        response = self._send(message)
        self.assertEqual(response, 'ACK\x0D\x0A')

    def test_storeallmode_boardErr(self, obs_mode='CustomCfg', err_board=3):
        message = f"DBE STOREALLMODE {obs_mode}\x0D\x0A"
        self._disable_board(err_board)
        response = self._send(message)
        self.assertEqual(response, f'ERR DBE BOARD {err_board} '
        'unreachable\x0D\x0A')

    def test_storeallmode_2boardErr(self, obs_mode='CustomCfg',
                                    err_board1=3, err_board2=2):
        message = f"DBE STOREALLMODE {obs_mode}\x0D\x0A"
        self._disable_board(err_board1)
        self._disable_board(err_board2)
        response = self._send(message)
        self.assertEqual(response, f'ERR DBE BOARD {err_board2} '
        f'{err_board1} unreachable\x0D\x0A')

    def test_storeallmode_cfgErr(self, obs_mode='MFS_7'):
        message = f"DBE STOREALLMODE {obs_mode}\x0D\x0A"
        response = self._send(message)
        self.assertEqual(response, 'ERR DBE writing cfg file\x0D\x0A')

    def test_storeallmode_bothErr(self, obs_mode='MFS_7', err_board=3):
        message = f"DBE STOREALLMODE {obs_mode}\x0D\x0A"
        self._disable_board(err_board)
        response = self._send(message)
        self.assertEqual(response, 'ERR DBE writing cfg file\x0D\x0A')

    def test_nak_storeall_missing(self):
        message = "DBE STOREALLMODE\x0D\x0A"
        response = self._send(message)
        self.assertEqual(response, 'NAK unknown command\x0D\x0A')

#      MODE, FIRM

    def test_mode_ok(self, board=1, obs_mode='MFS_7'):
        message = f"DBE MODE BOARD {board} {obs_mode}\x0D\x0A"
        response = self._send(message)
        self.assertEqual(response, 'ACK\x0D\x0A')

    def test_mode_boardErr(self, board=1, obs_mode='MFS_7'):
        message = f"DBE MODE BOARD {board} {obs_mode}\x0D\x0A"
        self._disable_board(board)
        response = self._send(message)
        self.assertEqual(response, f'ERR DBE BOARD {board} '
        'unreachable\x0D\x0A')

    def test_mode_cfgErr(self, board=1, obs_mode='PIPPO'):
        message = f"DBE MODE BOARD {board} {obs_mode}\x0D\x0A"
        response = self._send(message)
        self.assertEqual(response, 'ERR DBE CFG file not existing\x0D\x0A')

    def test_mode_bothErr(self, board=1, obs_mode='PIPPO'):
        message = f"DBE MODE BOARD {board} {obs_mode}\x0D\x0A"
        self._disable_board(board)
        response = self._send(message)
        self.assertEqual(response, 'ERR DBE CFG file not existing\x0D\x0A')

    def test_mode_noBoard(self, board=999, obs_mode='MFS_7'):
        message = f"DBE MODE BOARD {board} {obs_mode}\x0D\x0A"
        response = self._send(message)
        self.assertEqual(response, f'ERR DBE BOARD {board} '
        'not existing\x0D\x0A')

    def test_nak_mode_missing(self):
        message = "DBE MODE BOARD\x0D\x0A"
        response = self._send(message)
        self.assertEqual(response, 'NAK unknown command\x0D\x0A')

    def test_nak_mode_NotInt(self, obs_mode='MFS_7'):
        message = f"DBE MODE BOARD BOARD {obs_mode}\x0D\x0A"
        response = self._send(message)
        self.assertEqual(response, 'NAK unknown command\x0D\x0A')

    def test_firm_ok(self, board=1):
        message = f"DBE GETFIRM BOARD {board}\x0D\x0A"
        response = self._send(message)
        self.assertRegex(response, 'ACK\nBOARD [0-9]+ '
        'Prog=DBESM, Rev=rev [0-9]+.[0-9]+_[A-Za-z]+_[A-Za-z]+\r\n')

    def test_firm_boardErr(self, board=1):
        message = f"DBE GETFIRM BOARD {board}\x0D\x0A"
        self._disable_board(board)
        response = self._send(message)
        self.assertRegex(response, f'ERR DBE BOARD {board} '
        'unreachable\x0D\x0A')

    def test_firm_noBoard(self, board=999):
        message = f"DBE GETFIRM BOARD {board}\x0D\x0A"
        response = self._send(message)
        self.assertEqual(response, f'ERR DBE BOARD {board} '
        'not existing\x0D\x0A')

    def test_nak_firm_missing(self):
        message = "DBE GETFIRM BOARD\x0D\x0A"
        response = self._send(message)
        self.assertEqual(response, 'NAK unknown command\x0D\x0A')

    def test_nak_firm_NotInt(self):
        message = "DBE GETFIRM BOARD BOARD\x0D\x0A"
        response = self._send(message)
        self.assertEqual(response, 'NAK unknown command\x0D\x0A')

#      DIAG, GETSTATUS, GETCOMP

    def test_diag_ok(self, board=1):
        message = f"DBE ReadDIAG BOARD {board}\x0D\x0A"
        response = self._send(message)
        self.assertRegex(response, f'ACK\nBOARD {board}\n\n5V [0-9][.][0-9]+ '
        '3V3 [0-9][.][0-9]+\nT0 [0-9]+[.][0-9]+\r\n')

    def test_diag_boardErr(self, board=1):
        message = f"DBE ReadDIAG BOARD {board}\x0D\x0A"
        self._disable_board(board)
        response = self._send(message)
        self.assertEqual(response, f'ERR DBE BOARD {board} '
        'unreachable\x0D\x0A')

    def test_diag_noBoard(self, board=999):
        message = f"DBE ReadDIAG BOARD {board}\x0D\x0A"
        response = self._send(message)
        self.assertEqual(response, f'ERR DBE BOARD {board} '
        'not existing\x0D\x0A')

    def test_diag_noTemp(self, board=1):
        message = f"DBE ReadDIAG BOARD {board}\x0D\x0A"
        self._noTemp_board(board)
        response = self._send(message)
        self.assertRegex(response, f'ACK\nBOARD {board}\n\n5V [0-9][.][0-9]+ '
                '3V3 [0-9][.][0-9]+\ntemp sensor not present\r\n')

    def test_nak_diag_missing(self):
        message = "DBE ReadDIAG BOARD\x0D\x0A"
        response = self._send(message)
        self.assertEqual(response, 'NAK unknown command\x0D\x0A')

    def test_nak_diag_NotInt(self):
        message = "DBE ReadDIAG BOARD BOARD\x0D\x0A"
        response = self._send(message)
        self.assertEqual(response, 'NAK unknown command\x0D\x0A')

    def test_getstatus_ok(self, board=1):
        message = f"DBE GETSTATUS BOARD {board}\x0D\x0A"
        response = self._send(message)
        self.assertRegex(response, f'ACK\nBOARD {board}\n\nREG=[ [0-9]+ '
        '[0-9]+ [0-9]+ [0-9]+ [0-9]+ [0-9]+ [0-9]+ [0-9]+ [0-9]+ [0-9]+ ]\n'
        '\nATT=[ [0-9]+[.][05]  [0-9]+[.][05]  [0-9]+[.][05]  [0-9]+[.][05]'
        '  [0-9]+[.][05]  [0-9]+[.][05]  [0-9]+[.][05]  [0-9]+[.][05]  '
        '[0-9]+[.][05]  [0-9]+[.][05]  [0-9]+[.][05]  [0-9]+[.][05]  '
        '[0-9]+[.][05]  [0-9]+[.][05]  [0-9]+[.][05]  [0-9]+[.][05]  '
        '[0-9]+[.][05] ]\r\n')

    def test_getstatus_boardErr(self, board=1):
        message = f"DBE GETSTATUS BOARD {board}\x0D\x0A"
        self._disable_board(board)
        response = self._send(message)
        self.assertEqual(response, f'ERR DBE BOARD {board} '
        'unreachable\x0D\x0A')

    def test_getstatus_noBoard(self, board=999):
        message = f"DBE GETSTATUS BOARD {board}\x0D\x0A"
        response = self._send(message)
        self.assertEqual(response, f'ERR DBE BOARD {board} '
        'not existing\x0D\x0A')

    def test_nak_gestatus_missing(self):
        message = "DBE GETSTATUS BOARD\x0D\x0A"
        response = self._send(message)
        self.assertEqual(response, 'NAK unknown command\x0D\x0A')

    def test_nak_getstatus_NotInt(self):
        message = "DBE GETSTATUS BOARD BOARD\x0D\x0A"
        response = self._send(message)
        self.assertEqual(response, 'NAK unknown command\x0D\x0A')

    def test_getcomp_ok(self, board=1):
        message = f"DBE GETCOMP BOARD {board}\x0D\x0A"
        response = self._send(message)
        self.assertRegex(response, f'ACK\nBOARD {board}\n\nAMP')
        self.assertRegex(response, ' ]\r\n')
        self.assertEqual(len(response[21:39].split(" ")), 10)
        self.assertEqual(len(response[20:39]), 19)
        self.assertEqual(len(response[48:66].split(" ")), 10)
        self.assertEqual(len(response[47:66]), 19)
        self.assertEqual(len(response[76:96].split(" ")), 11)
        self.assertEqual(len(response[75:96]), 21)

    def test_getcomp_boardErr(self, board=1):
        message = f"DBE GETCOMP BOARD {board}\x0D\x0A"
        self._disable_board(board)
        response = self._send(message)
        self.assertEqual(response, f'ERR DBE BOARD {board} '
        'unreachable\x0D\x0A')

    def test_getcomp_noBoard(self, board=999):
        message = f"DBE GETCOMP BOARD {board}\x0D\x0A"
        response = self._send(message)
        self.assertEqual(response, f'ERR DBE BOARD {board} '
        'not existing\x0D\x0A')

    def test_nak_getcomp_missing(self):
        message = "DBE GETCOMP\x0D\x0A"
        response = self._send(message)
        self.assertEqual(response, 'NAK unknown command\x0D\x0A')

    def test_nak_getcomp_NotInt(self):
        message = "DBE GETCOMP BOARD BOARD\x0D\x0A"
        response = self._send(message)
        self.assertEqual(response, 'NAK unknown command\x0D\x0A')

#      SETATT

    def test_setatt_ok(self, ch=0, board=1, val=0.0):
        message = f"DBE SETATT {ch} BOARD {board} VALUE {val}\x0D\x0A"
        response = self._send(message)
        self.assertEqual(response, 'ACK\x0D\x0A')

    def test_setatt_ok_2(self, ch=0, board=1, val=.5):
        message = f"DBE SETATT {ch} BOARD {board} VALUE {val}\x0D\x0A"
        response = self._send(message)
        self.assertEqual(response, 'ACK\x0D\x0A')

    def test_setatt_ok_3(self, ch=0, board=1, val=1.000):
        message = f"DBE SETATT {ch} BOARD {board} VALUE {val}\x0D\x0A"
        response = self._send(message)
        self.assertEqual(response, 'ACK\x0D\x0A')

    def test_setatt_ok_4(self, ch=0, board=1, val=1):
        message = f"DBE SETATT {ch} BOARD {board} VALUE {val}\x0D\x0A"
        response = self._send(message)
        self.assertEqual(response, 'ACK\x0D\x0A')

    def test_setatt_chErr1(self, ch=17, board=1, val=0.0):
        message = f"DBE SETATT {ch} BOARD {board} VALUE {val}\x0D\x0A"
        response = self._send(message)
        self.assertEqual(response, f'ERR DBE ATT {ch} not existing\x0D\x0A')

    def test_setatt_chErr2(self, ch=0.0, board=1, val=0.0):
        message = f"DBE SETATT {ch} BOARD {board} VALUE {val}\x0D\x0A"
        response = self._send(message)
        self.assertEqual(response, 'NAK unknown command\x0D\x0A')

    def test_setatt_boardErr(self, ch=0, board=1, val=0.0):
        message = f"DBE SETATT {ch} BOARD {board} VALUE {val}\x0D\x0A"
        self._disable_board(board)
        response = self._send(message)
        self.assertEqual(response, f'ERR DBE BOARD {board} '
        'unreachable\x0D\x0A')

    def test_setatt_valErr1(self, ch=0, board=1, val=0.6):
        message = f"DBE SETATT {ch} BOARD {board} VALUE {val}\x0D\x0A"
        response = self._send(message)
        self.assertEqual(response, 'ERR DBE value out of range\x0D\x0A')

    def test_setatt_valErr2(self, ch=0, board=1, val=32.0):
        message = f"DBE SETATT {ch} BOARD {board} VALUE {val}\x0D\x0A"
        response = self._send(message)
        self.assertEqual(response, 'ERR DBE value out of range\x0D\x0A')

    def test_setatt_ChValErr(self, ch=17, board=1, val=0.6):
        message = f"DBE SETATT {ch} BOARD {board} VALUE {val}\x0D\x0A"
        response = self._send(message)
        self.assertEqual(response, f'ERR DBE ATT {ch} not existing\x0D\x0A')

    def test_setatt_BoardValErr(self, ch=1, board=1, val=0.6):
        message = f"DBE SETATT {ch} BOARD {board} VALUE {val}\x0D\x0A"
        self._disable_board(board)
        response = self._send(message)
        self.assertEqual(response, 'ERR DBE value out of range\x0D\x0A')

    def test_setatt_AllErr(self, ch=17, board=1, val=0.6):
        message = f"DBE SETATT {ch} BOARD {board} VALUE {val}\x0D\x0A"
        self._disable_board(board)
        response = self._send(message)
        self.assertEqual(response, f'ERR DBE ATT {ch} not existing\x0D\x0A')

    def test_setatt_noBoard(self, ch=0, board=999, val=0.0):
        message = f"DBE SETATT {ch} BOARD {board} VALUE {val}\x0D\x0A"
        response = self._send(message)
        self.assertEqual(response, f'ERR DBE BOARD {board} '
        'not existing\x0D\x0A')

    def test_setatt_noBoard_ChValErr(self, ch=17, board=999, val=0.6):
        message = f"DBE SETATT {ch} BOARD {board} VALUE {val}\x0D\x0A"
        response = self._send(message)
        self.assertEqual(response, f'ERR DBE BOARD {board} '
        'not existing\x0D\x0A')

    def test_nak_setatt_missing(self):
        message = "DBE SETATT\x0D\x0A"
        response = self._send(message)
        self.assertEqual(response, 'NAK unknown command\x0D\x0A')

    def test_nak_setatt_NotInt(self):
        message = "DBE SETATT 1 BOARD BOARD VALUE 0\x0D\x0A"
        response = self._send(message)
        self.assertEqual(response, 'NAK unknown command\x0D\x0A')

#      SETAMP

    def test_setamp_ok(self, ch=1, board=1, val=0):
        message = f"DBE SETAMP {ch} BOARD {board} VALUE {val}\x0D\x0A"
        response = self._send(message)
        self.assertEqual(response, 'ACK\x0D\x0A')

    def test_setamp_chErr1(self, ch=11, board=1, val=0):
        message = f"DBE SETAMP {ch} BOARD {board} VALUE {val}\x0D\x0A"
        response = self._send(message)
        self.assertEqual(response, f'ERR DBE AMP {ch} not existing\x0D\x0A')

    def test_setamp_chErr2(self, ch=1.0, board=1, val=0):
        message = f"DBE SETAMP {ch} BOARD {board} VALUE {val}\x0D\x0A"
        response = self._send(message)
        self.assertEqual(response, 'NAK unknown command\x0D\x0A')

    def test_setamp_boardErr(self, ch=1, board=1, val=0):
        message = f"DBE SETAMP {ch} BOARD {board} VALUE {val}\x0D\x0A"
        self._disable_board(board)
        response = self._send(message)
        self.assertEqual(response, f'ERR DBE BOARD {board} '
        'unreachable\x0D\x0A')

    def test_setamp_valErr1(self, ch=1, board=1, val=0.6):
        message = f"DBE SETAMP {ch} BOARD {board} VALUE {val}\x0D\x0A"
        response = self._send(message)
        self.assertEqual(response, 'ERR DBE value out of range\x0D\x0A')

    def test_setamp_valErr2(self, ch=1, board=1, val=2):
        message = f"DBE SETAMP {ch} BOARD {board} VALUE {val}\x0D\x0A"
        response = self._send(message)
        self.assertEqual(response, 'ERR DBE value out of range\x0D\x0A')

    def test_setamp_ChValErr(self, ch=11, board=1, val=2):
        message = f"DBE SETAMP {ch} BOARD {board} VALUE {val}\x0D\x0A"
        response = self._send(message)
        self.assertEqual(response, f'ERR DBE AMP {ch} not existing\x0D\x0A')

    def test_setamp_AllErr(self, ch=11, board=1, val=2):
        message = f"DBE SETAMP {ch} BOARD {board} VALUE {val}\x0D\x0A"
        self._disable_board(board)
        response = self._send(message)
        self.assertEqual(response, f'ERR DBE AMP {ch} not existing\x0D\x0A')

    def test_setamp_noBoard(self, ch=0, board=999, val=0):
        message = f"DBE SETAMP {ch} BOARD {board} VALUE {val}\x0D\x0A"
        response = self._send(message)
        self.assertEqual(response, f'ERR DBE BOARD {board} '
        'not existing\x0D\x0A')

    def test_nak_setamp_missing(self):
        message = "DBE SETAMP\x0D\x0A"
        response = self._send(message)
        self.assertEqual(response, 'NAK unknown command\x0D\x0A')

    def test_nak_setamp_NotInt(self):
        message = "DBE SETAMP 1 BOARD BOARD VALUE 0\x0D\x0A"
        response = self._send(message)
        self.assertEqual(response, 'NAK unknown command\x0D\x0A')

#      SETEQ

    def test_seteq_ok(self, ch=1, board=1, val=0):
        message = f"DBE SETEQ {ch} BOARD {board} VALUE {val}\x0D\x0A"
        response = self._send(message)
        self.assertEqual(response, 'ACK\x0D\x0A')

    def test_seteq_chErr1(self, ch=11, board=1, val=0):
        message = f"DBE SETEQ {ch} BOARD {board} VALUE {val}\x0D\x0A"
        response = self._send(message)
        self.assertEqual(response, f'ERR DBE EQ {ch} not existing\x0D\x0A')

    def test_seteq_chErr2(self, ch=1.0, board=1, val=0):
        message = f"DBE SETEQ {ch} BOARD {board} VALUE {val}\x0D\x0A"
        response = self._send(message)
        self.assertEqual(response, 'NAK unknown command\x0D\x0A')

    def test_seteq_boardErr(self, ch=1, board=1, val=0):
        message = f"DBE SETEQ {ch} BOARD {board} VALUE {val}\x0D\x0A"
        self._disable_board(board)
        response = self._send(message)
        self.assertEqual(response, f'ERR DBE BOARD {board} '
        'unreachable\x0D\x0A')

    def test_seteq_valErr1(self, ch=1, board=1, val=0.6):
        message = f"DBE SETEQ {ch} BOARD {board} VALUE {val}\x0D\x0A"
        response = self._send(message)
        self.assertEqual(response, 'ERR DBE value out of range\x0D\x0A')

    def test_seteq_valErr2(self, ch=1, board=1, val=2):
        message = f"DBE SETEQ {ch} BOARD {board} VALUE {val}\x0D\x0A"
        response = self._send(message)
        self.assertEqual(response, 'ERR DBE value out of range\x0D\x0A')

    def test_seteq_ChValErr(self, ch=11, board=1, val=2):
        message = f"DBE SETEQ {ch} BOARD {board} VALUE {val}\x0D\x0A"
        response = self._send(message)
        self.assertEqual(response, f'ERR DBE EQ {ch} not existing\x0D\x0A')

    def test_seteq_AllErr(self, ch=11, board=1, val=2):
        message = f"DBE SETEQ {ch} BOARD {board} VALUE {val}\x0D\x0A"
        self._disable_board(board)
        response = self._send(message)
        self.assertEqual(response, f'ERR DBE EQ {ch} not existing\x0D\x0A')

    def test_seteq_noBoard(self, ch=0, board=999, val=0):
        message = f"DBE SETEQ {ch} BOARD {board} VALUE {val}\x0D\x0A"
        response = self._send(message)
        self.assertEqual(response, f'ERR DBE BOARD {board} '
        'not existing\x0D\x0A')

    def test_nak_seteq_missing(self):
        message = "DBE SETEQ\x0D\x0A"
        response = self._send(message)
        self.assertEqual(response, 'NAK unknown command\x0D\x0A')

    def test_nak_seteq_NotInt(self):
        message = "DBE SETEQ 1 BOARD BOARD VALUE 0\x0D\x0A"
        response = self._send(message)
        self.assertEqual(response, 'NAK unknown command\x0D\x0A')

#      SETBPF

    def test_setbpf_ok_1a(self, ch='1a', board=1, val=0):
        message = f"DBE SETBPF {ch} BOARD {board} VALUE {val}\x0D\x0A"
        response = self._send(message)
        self.assertEqual(response, 'ACK\x0D\x0A')

    def test_setbpf_ok_1b(self, ch='1b', board=1, val=0):
        message = f"DBE SETBPF {ch} BOARD {board} VALUE {val}\x0D\x0A"
        response = self._send(message)
        self.assertEqual(response, 'ACK\x0D\x0A')

    def test_setbpf_ok_2(self, ch='2', board=1, val=0):
        message = f"DBE SETBPF {ch} BOARD {board} VALUE {val}\x0D\x0A"
        response = self._send(message)
        self.assertEqual(response, 'ACK\x0D\x0A')

    def test_setbpf_chErr1(self, ch=11, board=1, val=0):
        message = f"DBE SETBPF {ch} BOARD {board} VALUE {val}\x0D\x0A"
        response = self._send(message)
        self.assertEqual(response, f'ERR DBE BPF {ch} not existing\x0D\x0A')

    def test_setbpf_chErr2(self, ch='111a', board=1, val=0):
        message = f"DBE SETBPF {ch} BOARD {board} VALUE {val}\x0D\x0A"
        response = self._send(message)
        self.assertEqual(response, f'ERR DBE BPF {ch} not existing\x0D\x0A')

    def test_setbpf_chErr3(self, ch='1a2', board=1, val=0):
        message = f"DBE SETBPF {ch} BOARD {board} VALUE {val}\x0D\x0A"
        response = self._send(message)
        self.assertEqual(response, 'NAK unknown command\x0D\x0A')

    def test_setbpf_chErr4(self, ch='a1', board=1, val=0):
        message = f"DBE SETBPF {ch} BOARD {board} VALUE {val}\x0D\x0A"
        response = self._send(message)
        self.assertEqual(response, 'NAK unknown command\x0D\x0A')

    def test_setbpf_chErr5(self, ch='1aa', board=1, val=0):
        message = f"DBE SETBPF {ch} BOARD {board} VALUE {val}\x0D\x0A"
        response = self._send(message)
        self.assertEqual(response, 'NAK unknown command\x0D\x0A')

    def test_setbpf_chErr6(self, ch='a', board=1, val=0):
        message = f"DBE SETBPF {ch} BOARD {board} VALUE {val}\x0D\x0A"
        response = self._send(message)
        self.assertEqual(response, 'NAK unknown command\x0D\x0A')

    def test_setbpf_boardErr(self, ch='1a', board=1, val=0):
        message = f"DBE SETBPF {ch} BOARD {board} VALUE {val}\x0D\x0A"
        self._disable_board(board)
        response = self._send(message)
        self.assertEqual(response, f'ERR DBE BOARD {board} '
        'unreachable\x0D\x0A')

    def test_setbpf_valErr1(self, ch='1a', board=1, val=0.6):
        message = f"DBE SETBPF {ch} BOARD {board} VALUE {val}\x0D\x0A"
        response = self._send(message)
        self.assertEqual(response, 'ERR DBE value out of range\x0D\x0A')

    def test_setbpf_valErr2(self, ch='1a', board=1, val=2):
        message = f"DBE SETBPF {ch} BOARD {board} VALUE {val}\x0D\x0A"
        response = self._send(message)
        self.assertEqual(response, 'ERR DBE value out of range\x0D\x0A')

    def test_setbpf_ChValErr(self, ch=11, board=1, val=2):
        message = f"DBE SETBPF {ch} BOARD {board} VALUE {val}\x0D\x0A"
        response = self._send(message)
        self.assertEqual(response, f'ERR DBE BPF {ch} not existing\x0D\x0A')

    def test_setbpf_AllErr(self, ch=11, board=1, val=2):
        message = f"DBE SETBPF {ch} BOARD {board} VALUE {val}\x0D\x0A"
        self._disable_board(board)
        response = self._send(message)
        self.assertEqual(response, f'ERR DBE BPF {ch} not existing\x0D\x0A')

    def test_setbpf_noBoard(self, ch=0, board=999, val=0):
        message = f"DBE SETBPF {ch} BOARD {board} VALUE {val}\x0D\x0A"
        response = self._send(message)
        self.assertEqual(response, f'ERR DBE BOARD {board} '
        'not existing\x0D\x0A')

    def test_nak_setbpf_missing(self):
        message = "DBE SETBPF\x0D\x0A"
        response = self._send(message)
        self.assertEqual(response, 'NAK unknown command\x0D\x0A')

    def test_nak_setbpf_NotInt(self):
        message = "DBE SETBPF 1a BOARD BOARD VALUE 0\x0D\x0A"
        response = self._send(message)
        self.assertEqual(response, 'NAK unknown command\x0D\x0A')

#      GETCFG, SETDBEATT

    def test_getcfg_ok(self):
        message = "DBE GETCFG\x0D\x0A"
        response = self._send(message)
        self.assertRegex(response, 'ACK\nBOARD [0-9]+')
        self.assertRegex(response, '\n\nBOARD [0-9]+')
        self.assertRegex(response, '\n\nBOARD [0-9]+')
        self.assertRegex(response, '\n\nBOARD [0-9]+')
        self.assertRegex(response, '\r\n')

    def test_getcfg_boardErr(self, err_board=3):
        self._disable_board(err_board)
        message = "DBE GETCFG\x0D\x0A"
        response = self._send(message)
        self.assertRegex(response, f'\nBOARD {err_board} '
        'ERR DBE BOARD unreachable')

    def test_nak_getcfg_plus(self):
        message = "DBE GETCFG BOARD 0\x0D\x0A"
        response = self._send(message)
        self.assertEqual(response, 'NAK unknown command\x0D\x0A')

    def test_setdbeatt_single(self, out_dbe='1_DBBC2'):
        message = f"DBE SETDBEATT {out_dbe} 1.0\x0D\x0A"
        response = self._send(message)
        self.assertRegex(response, f'DBE {out_dbe} BOARD [0-9]+ ACK\r\n')

    def test_setdbeatt_single_plus3_ok(self, out_dbe='1_DBBC2'):
        message1 = f"DBE SETDBEATT {out_dbe} 1.0\x0D\x0A"
        self._send(message1)
        message2 = f"DBE SETDBEATT {out_dbe} +3\x0D\x0A"
        response = self._send(message2)
        self.assertRegex(response, f'DBE {out_dbe} BOARD [0-9]+ ACK\r\n')

    def test_setdbeatt_single_plus3_err(self, out_dbe='1_DBBC2'):
        message1 = f"DBE SETDBEATT {out_dbe} 31.0\x0D\x0A"
        self._send(message1)
        message2 = f"DBE SETDBEATT {out_dbe} +3\x0D\x0A"
        response = self._send(message2)
        self.assertRegex(response, f'ERR DBE {out_dbe} BOARD '
        '[0-9]+ value out of range\r\n')

    def test_setdbeatt_single_minus3_ok(self, out_dbe='1_DBBC2'):
        message1 = f"DBE SETDBEATT {out_dbe} 4.0\x0D\x0A"
        self._send(message1)
        message2 = f"DBE SETDBEATT {out_dbe} -3\x0D\x0A"
        response = self._send(message2)
        self.assertRegex(response, f'DBE {out_dbe} BOARD [0-9]+ ACK\r\n')

    def test_setdbeatt_single_minus3_err(self, out_dbe='1_DBBC2'):
        message1 = f"DBE SETDBEATT {out_dbe} 1.0\x0D\x0A"
        self._send(message1)
        message2 = f"DBE SETDBEATT {out_dbe} -3\x0D\x0A"
        response = self._send(message2)
        self.assertRegex(response, f'ERR DBE {out_dbe} BOARD '
        '[0-9]+ value out of range\r\n')

    def test_setdbeatt_mult(self, out_dbe='prova'):
        message = f"DBE SETDBEATT {out_dbe} 1.0\x0D\x0A"
        response = self._send(message)
        self.assertRegex(response, f'DBE {out_dbe} BOARD [0-9]+ ACK\r\n')
        self.assertRegex(response, f'DBE {out_dbe} BOARD [0-9]+ ACK\r\n')

    def test_setdbeatt_mult_minus3(self, out_dbe='prova'):
        message1 = f"DBE SETDBEATT {out_dbe} 4.0\x0D\x0A"
        self._send(message1)
        message2 = f"DBE SETDBEATT {out_dbe} -3\x0D\x0A"
        response = self._send(message2)
        self.assertRegex(response, f'DBE {out_dbe} BOARD [0-9]+ ACK\r\n')
        self.assertRegex(response, f'DBE {out_dbe} BOARD [0-9]+ ACK\r\n')

    def test_setdbeatt_mult_minus3_err(self, out_dbe='prova'):
        message1 = f"DBE SETDBEATT {out_dbe} 1.0\x0D\x0A"
        self._send(message1)
        message2 = f"DBE SETDBEATT {out_dbe} -3\x0D\x0A"
        response = self._send(message2)
        self.assertRegex(response, f'DBE {out_dbe} BOARD '
        '[0-9]+ value out of range\r\n')
        self.assertRegex(response, f'DBE {out_dbe} BOARD '
        '[0-9]+ value out of range\r\n')

    def test_setdbeatt_single_ValErr(self, out_dbe='1_DBBC2'):
        message = f"DBE SETDBEATT {out_dbe} 32\x0D\x0A"
        response = self._send(message)
        self.assertRegex(response, f'ERR DBE {out_dbe} BOARD '
        '[0-9]+ value out of range\r\n')

    def test_setdbeatt_mult_ValErr(self, out_dbe='prova'):
        message = f"DBE SETDBEATT {out_dbe} 32\x0D\x0A"
        response = self._send(message)
        self.assertRegex(response, f'ERR DBE {out_dbe} BOARD '
        '[0-9]+ value out of range\r\n')
        self.assertRegex(response, f'ERR DBE {out_dbe} BOARD '
        '[0-9]+ value out of range\r\n')

    def test_setdbeatt_boardErr(self, out_dbe='SARDA_14', err_board=4):
        self._disable_board(err_board)
        message = f"DBE SETDBEATT {out_dbe} 1.0\x0D\x0A"
        response = self._send(message)
        self.assertRegex(response, f'ERR DBE {out_dbe} BOARD {err_board}'
        ' unreachable\r\n')

    def test_setdbeatt_outErr(self, out_dbe='NOTHING'):
        message = f"DBE SETDBEATT {out_dbe} 1.0\x0D\x0A"
        response = self._send(message)
        self.assertEqual(response, 'ERR DBE Output not existing\r\n')

    def test_setdbeatt_boardOutErr(self, out_dbe='NOTHING', err_board=4):
        self._disable_board(err_board)
        message = f"DBE SETDBEATT {out_dbe} 1.0\x0D\x0A"
        response = self._send(message)
        self.assertEqual(response, 'ERR DBE Output not existing\r\n')

    def test_setdbeatt_boardValErr(self, out_dbe='SARDA_14', err_board=4):
        self._disable_board(err_board)
        message = f"DBE SETDBEATT {out_dbe} 32\x0D\x0A"
        response = self._send(message)
        self.assertRegex(response, f'ERR DBE {out_dbe} BOARD {err_board}'
        ' value out of range\r\n')

    def test_nak_setdbeatt(self, out_dbe='1_DBBC2'):
        message = f"DBE SETDBEATT {out_dbe}\x0D\x0A"
        response = self._send(message)
        self.assertEqual(response, 'NAK unknown command\x0D\x0A')

#       GETDBEATT, FIRM

    def test_getdbeatt_single(self, out_dbe='1_DBBC2'):
        message = f"DBE GETDBEATT {out_dbe}\x0D\x0A"
        response = self._send(message)
        self.assertRegex(response, f'ACK {out_dbe} BOARD [0-9]+ '
        'ATT [0-9]+ VALUE [0-9]+.[0-9]+\r\n')

    def test_getdbeatt_mult(self, out_dbe='prova'):
        message = f"DBE GETDBEATT {out_dbe}\x0D\x0A"
        response = self._send(message)
        self.assertRegex(response, f'ACK {out_dbe} BOARD [0-9]+ '
        'ATT [0-9]+ VALUE [0-9]+.[0-9]+\r\n')
        self.assertRegex(response, f'ACK {out_dbe} BOARD [0-9]+ '
        'ATT [0-9]+ VALUE [0-9]+.[0-9]+\r\n')

    def test_getdbeatt_boardErr(self, out_dbe='SARDA_14', err_board=4):
        self._disable_board(err_board)
        message = f"DBE GETDBEATT {out_dbe}\x0D\x0A"
        response = self._send(message)
        self.assertRegex(response, f'ERR DBE {out_dbe} BOARD {err_board}'
        ' unreachable\r\n')

    def test_getdbeatt_outErr(self, out_dbe='NOTHING'):
        message = f"DBE GETDBEATT {out_dbe}\x0D\x0A"
        response = self._send(message)
        self.assertEqual(response, 'ERR DBE Output not existing\r\n')

    def test_getdbeatt_boardOutErr(self, out_dbe='NOTHING', err_board=4):
        self._disable_board(err_board)
        message = f"DBE GETDBEATT {out_dbe}\x0D\x0A"
        response = self._send(message)
        self.assertEqual(response, 'ERR DBE Output not existing\r\n')

    def test_nak_getdbeatt(self):
        message = "DBE GETDBEATT\x0D\x0A"
        response = self._send(message)
        self.assertEqual(response, 'NAK unknown command\x0D\x0A')

#       SETDBEAMP

    def test_setdbeamp_single_on(self, out_dbe='1_DBBC2'):
        message = f"DBE SETDBEAMP {out_dbe} 1\x0D\x0A"
        response = self._send(message)
        self.assertRegex(response, f'DBE {out_dbe} BOARD [0-9]+ ACK\r\n')

    def test_setdbeamp_single_off(self, out_dbe='1_DBBC2'):
        message = f"DBE SETDBEAMP {out_dbe} 0\x0D\x0A"
        response = self._send(message)
        self.assertRegex(response, f'DBE {out_dbe} BOARD [0-9]+ ACK\r\n')

    def test_setdbeamp_mult_on(self, out_dbe='prova'):
        message = f"DBE SETDBEAMP {out_dbe} 1\x0D\x0A"
        response = self._send(message)
        self.assertRegex(response, f'DBE {out_dbe} BOARD [0-9]+ ACK\r\n')
        self.assertRegex(response, f'DBE {out_dbe} BOARD [0-9]+ ACK\r\n')

    def test_setdbeamp_mult_off(self, out_dbe='prova'):
        message = f"DBE SETDBEAMP {out_dbe} 0\x0D\x0A"
        response = self._send(message)
        self.assertRegex(response, f'DBE {out_dbe} BOARD [0-9]+ ACK\r\n')
        self.assertRegex(response, f'DBE {out_dbe} BOARD [0-9]+ ACK\r\n')

    def test_setdbeamp_single_IntValErr(self, out_dbe='1_DBBC2'):
        message = f"DBE SETDBEAMP {out_dbe} 2\x0D\x0A"
        response = self._send(message)
        self.assertRegex(response, f'ERR DBE {out_dbe} BOARD '
        '[0-9]+ value out of range\r\n')

    def test_setdbeamp_single_FloatValErr(self, out_dbe='1_DBBC2'):
        message = f"DBE SETDBEAMP {out_dbe} 1.5\x0D\x0A"
        response = self._send(message)
        self.assertRegex(response, f'ERR DBE {out_dbe} BOARD '
        '[0-9]+ value out of range\r\n')

    def test_setdbeamp_mult_IntValErr(self, out_dbe='prova'):
        message = f"DBE SETDBEAMP {out_dbe} 2\x0D\x0A"
        response = self._send(message)
        self.assertRegex(response, f'ERR DBE {out_dbe} BOARD '
        '[0-9]+ value out of range\r\n')
        self.assertRegex(response, f'ERR DBE {out_dbe} BOARD '
        '[0-9]+ value out of range\r\n')

    def test_setdbeamp_mult_FloatValErr(self, out_dbe='prova'):
        message = f"DBE SETDBEAMP {out_dbe} 1.5\x0D\x0A"
        response = self._send(message)
        self.assertRegex(response, f'ERR DBE {out_dbe} BOARD '
        '[0-9]+ value out of range\r\n')
        self.assertRegex(response, f'ERR DBE {out_dbe} BOARD '
        '[0-9]+ value out of range\r\n')

    def test_setdbeamp_boardErr(self, out_dbe='SARDA_14', err_board=4):
        self._disable_board(err_board)
        message = f"DBE SETDBEAMP {out_dbe} 1\x0D\x0A"
        response = self._send(message)
        self.assertRegex(response, f'ERR DBE {out_dbe} BOARD {err_board}'
        ' unreachable\r\n')

    def test_setdbeamp_outErr(self, out_dbe='NOTHING'):
        message = f"DBE SETDBEAMP {out_dbe} 1\x0D\x0A"
        response = self._send(message)
        self.assertEqual(response, 'ERR DBE Output not existing\r\n')

    def test_setdbeamp_boardOutErr(self, out_dbe='NOTHING', err_board=4):
        self._disable_board(err_board)
        message = f"DBE SETDBEAMP {out_dbe} 1\x0D\x0A"
        response = self._send(message)
        self.assertEqual(response, 'ERR DBE Output not existing\r\n')

    def test_setdbeamp_boardValErr(self, out_dbe='SARDA_14', err_board=4):
        self._disable_board(err_board)
        message = f"DBE SETDBEAMP {out_dbe} 2\x0D\x0A"
        response = self._send(message)
        self.assertRegex(response, f'ERR DBE {out_dbe} BOARD {err_board}'
        ' value out of range\r\n')

    def test_nak_setdbeamp(self, out_dbe='1_DBBC2'):
        message = f"DBE SETDBEAMP {out_dbe}\x0D\x0A"
        response = self._send(message)
        self.assertEqual(response, 'NAK unknown command\x0D\x0A')

#       GETDBEAMP

    def test_getdbeamp_single(self, out_dbe='1_DBBC2'):
        message = f"DBE GETDBEAMP {out_dbe}\x0D\x0A"
        response = self._send(message)
        self.assertRegex(response, f'ACK {out_dbe} BOARD [0-9]+ '
        'AMP [0-9]+ VALUE [0-9]+\r\n')

    def test_getdbeamp_mult(self, out_dbe='prova'):
        message = f"DBE GETDBEAMP {out_dbe}\x0D\x0A"
        response = self._send(message)
        self.assertRegex(response, f'ACK {out_dbe} BOARD [0-9]+ '
        'AMP [0-9]+ VALUE [0-9]+\r\n')
        self.assertRegex(response, f'ACK {out_dbe} BOARD [0-9]+ '
        'AMP [0-9]+ VALUE [0-9]+\r\n')

    def test_getdbeamp_boardErr(self, out_dbe='SARDA_14', err_board=4):
        self._disable_board(err_board)
        message = f"DBE GETDBEAMP {out_dbe}\x0D\x0A"
        response = self._send(message)
        self.assertRegex(response, f'ERR DBE {out_dbe} BOARD {err_board}'
        ' unreachable\r\n')

    def test_getdbeamp_outErr(self, out_dbe='NOTHING'):
        message = f"DBE GETDBEAMP {out_dbe}\x0D\x0A"
        response = self._send(message)
        self.assertEqual(response, 'ERR DBE Output not existing\r\n')

    def test_getdbeamp_boardOutErr(self, out_dbe='NOTHING', err_board=4):
        self._disable_board(err_board)
        message = f"DBE GETDBEAMP {out_dbe}\x0D\x0A"
        response = self._send(message)
        self.assertEqual(response, 'ERR DBE Output not existing\r\n')

    def test_nak_getdbeamp(self):
        message = "DBE GETDBEAMP\x0D\x0A"
        response = self._send(message)
        self.assertEqual(response, 'NAK unknown command\x0D\x0A')

#       SETDBEEQ

    def test_setdbeeq_single_on(self, out_dbe='1_DBBC2'):
        message = f"DBE SETDBEEQ {out_dbe} 1\x0D\x0A"
        response = self._send(message)
        self.assertRegex(response, f'DBE {out_dbe} BOARD [0-9]+ ACK\r\n')

    def test_setdbeeq_single_off(self, out_dbe='1_DBBC2'):
        message = f"DBE SETDBEEQ {out_dbe} 0\x0D\x0A"
        response = self._send(message)
        self.assertRegex(response, f'DBE {out_dbe} BOARD [0-9]+ ACK\r\n')

    def test_setdbeeq_mult_on(self, out_dbe='prova'):
        message = f"DBE SETDBEEQ {out_dbe} 1\x0D\x0A"
        response = self._send(message)
        self.assertRegex(response, f'DBE {out_dbe} BOARD [0-9]+ ACK\r\n')
        self.assertRegex(response, f'DBE {out_dbe} BOARD [0-9]+ ACK\r\n')

    def test_setdbeeq_mult_off(self, out_dbe='prova'):
        message = f"DBE SETDBEEQ {out_dbe} 0\x0D\x0A"
        response = self._send(message)
        self.assertRegex(response, f'DBE {out_dbe} BOARD [0-9]+ ACK\r\n')
        self.assertRegex(response, f'DBE {out_dbe} BOARD [0-9]+ ACK\r\n')

    def test_setdbeeq_single_IntValErr(self, out_dbe='1_DBBC2'):
        message = f"DBE SETDBEEQ {out_dbe} 2\x0D\x0A"
        response = self._send(message)
        self.assertRegex(response, f'ERR DBE {out_dbe} BOARD '
        '[0-9]+ value out of range\r\n')

    def test_setdbeeq_single_FloatValErr(self, out_dbe='1_DBBC2'):
        message = f"DBE SETDBEEQ {out_dbe} 1.5\x0D\x0A"
        response = self._send(message)
        self.assertRegex(response, f'ERR DBE {out_dbe} BOARD '
        '[0-9]+ value out of range\r\n')

    def test_setdbeeq_mult_IntValErr(self, out_dbe='prova'):
        message = f"DBE SETDBEEQ {out_dbe} 2\x0D\x0A"
        response = self._send(message)
        self.assertRegex(response, f'ERR DBE {out_dbe} BOARD '
        '[0-9]+ value out of range\r\n')
        self.assertRegex(response, f'ERR DBE {out_dbe} BOARD '
        '[0-9]+ value out of range\r\n')

    def test_setdbeeq_mult_FloatValErr(self, out_dbe='prova'):
        message = f"DBE SETDBEEQ {out_dbe} 1.5\x0D\x0A"
        response = self._send(message)
        self.assertRegex(response, f'ERR DBE {out_dbe} BOARD '
        '[0-9]+ value out of range\r\n')
        self.assertRegex(response, f'ERR DBE {out_dbe} BOARD '
        '[0-9]+ value out of range\r\n')

    def test_setdbeeq_boardErr(self, out_dbe='SARDA_14', err_board=4):
        self._disable_board(err_board)
        message = f"DBE SETDBEEQ {out_dbe} 1\x0D\x0A"
        response = self._send(message)
        self.assertRegex(response, f'ERR DBE {out_dbe} BOARD {err_board}'
        ' unreachable\r\n')

    def test_setdbeeq_outErr(self, out_dbe='NOTHING'):
        message = f"DBE SETDBEEQ {out_dbe} 1\x0D\x0A"
        response = self._send(message)
        self.assertEqual(response, 'ERR DBE Output not existing\r\n')

    def test_setdbeeq_boardOutErr(self, out_dbe='NOTHING', err_board=4):
        self._disable_board(err_board)
        message = f"DBE SETDBEEQ {out_dbe} 1\x0D\x0A"
        response = self._send(message)
        self.assertEqual(response, 'ERR DBE Output not existing\r\n')

    def test_setdbeeq_boardValErr(self, out_dbe='SARDA_14', err_board=4):
        self._disable_board(err_board)
        message = f"DBE SETDBEEQ {out_dbe} 2\x0D\x0A"
        response = self._send(message)
        self.assertRegex(response, f'ERR DBE {out_dbe} BOARD {err_board}'
        ' value out of range\r\n')

    def test_nak_setdbeeq(self, out_dbe='1_DBBC2'):
        message = f"DBE SETDBEEQ {out_dbe}\x0D\x0A"
        response = self._send(message)
        self.assertEqual(response, 'NAK unknown command\x0D\x0A')

#       GETDBEEQ

    def test_getdbeeq_single(self, out_dbe='1_DBBC2'):
        message = f"DBE GETDBEEQ {out_dbe}\x0D\x0A"
        response = self._send(message)
        self.assertRegex(response, f'ACK {out_dbe} BOARD [0-9]+ '
        'EQ [0-9]+ VALUE [0-9]+\r\n')

    def test_getdbeeq_mult(self, out_dbe='prova'):
        message = f"DBE GETDBEEQ {out_dbe}\x0D\x0A"
        response = self._send(message)
        self.assertRegex(response, f'ACK {out_dbe} BOARD [0-9]+ '
        'EQ [0-9]+ VALUE [0-9]+\r\n')
        self.assertRegex(response, f'ACK {out_dbe} BOARD [0-9]+ '
        'EQ [0-9]+ VALUE [0-9]+\r\n')

    def test_getdbeeq_boardErr(self, out_dbe='SARDA_14', err_board=4):
        self._disable_board(err_board)
        message = f"DBE GETDBEEQ {out_dbe}\x0D\x0A"
        response = self._send(message)
        self.assertRegex(response, f'ERR DBE {out_dbe} BOARD {err_board}'
        ' unreachable\r\n')

    def test_getdbeeq_outErr(self, out_dbe='NOTHING'):
        message = f"DBE GETDBEEQ {out_dbe}\x0D\x0A"
        response = self._send(message)
        self.assertEqual(response, 'ERR DBE Output not existing\r\n')

    def test_getdbeeq_boardOutErr(self, out_dbe='NOTHING', err_board=4):
        self._disable_board(err_board)
        message = f"DBE GETDBEEQ {out_dbe}\x0D\x0A"
        response = self._send(message)
        self.assertEqual(response, 'ERR DBE Output not existing\r\n')

    def test_nak_getdbeeq(self):
        message = "DBE GETDBEEQ\x0D\x0A"
        response = self._send(message)
        self.assertEqual(response, 'NAK unknown command\x0D\x0A')

#       SETDBEBPF

    def test_setdbebpf_single_on(self, out_dbe='1_DBBC2'):
        message = f"DBE SETDBEBPF {out_dbe} 1\x0D\x0A"
        response = self._send(message)
        self.assertRegex(response, f'DBE {out_dbe} BOARD [0-9]+ ACK\r\n')

    def test_setdbebpf_single_off(self, out_dbe='1_DBBC2'):
        message = f"DBE SETDBEBPF {out_dbe} 0\x0D\x0A"
        response = self._send(message)
        self.assertRegex(response, f'DBE {out_dbe} BOARD [0-9]+ ACK\r\n')

    def test_setdbebpf_mult_on(self, out_dbe='prova'):
        message = f"DBE SETDBEBPF {out_dbe} 1\x0D\x0A"
        response = self._send(message)
        self.assertRegex(response, f'DBE {out_dbe} BOARD [0-9]+ ACK\r\n')
        self.assertRegex(response, f'DBE {out_dbe} BOARD [0-9]+ ACK\r\n')

    def test_setdbebpf_mult_off(self, out_dbe='prova'):
        message = f"DBE SETDBEBPF {out_dbe} 0\x0D\x0A"
        response = self._send(message)
        self.assertRegex(response, f'DBE {out_dbe} BOARD [0-9]+ ACK\r\n')
        self.assertRegex(response, f'DBE {out_dbe} BOARD [0-9]+ ACK\r\n')

    def test_setdbebpf_single_IntValErr(self, out_dbe='1_DBBC2'):
        message = f"DBE SETDBEBPF {out_dbe} 2\x0D\x0A"
        response = self._send(message)
        self.assertRegex(response, f'ERR DBE {out_dbe} BOARD '
        '[0-9]+ value out of range\r\n')

    def test_setdbebpf_single_FloatValErr(self, out_dbe='1_DBBC2'):
        message = f"DBE SETDBEBPF {out_dbe} 1.5\x0D\x0A"
        response = self._send(message)
        self.assertRegex(response, f'ERR DBE {out_dbe} BOARD '
        '[0-9]+ value out of range\r\n')

    def test_setdbebpf_mult_IntValErr(self, out_dbe='prova'):
        message = f"DBE SETDBEBPF {out_dbe} 2\x0D\x0A"
        response = self._send(message)
        self.assertRegex(response, f'ERR DBE {out_dbe} BOARD '
        '[0-9]+ value out of range\r\n')
        self.assertRegex(response, f'ERR DBE {out_dbe} BOARD '
        '[0-9]+ value out of range\r\n')

    def test_setdbebpf_mult_FloatValErr(self, out_dbe='prova'):
        message = f"DBE SETDBEBPF {out_dbe} 1.5\x0D\x0A"
        response = self._send(message)
        self.assertRegex(response, f'ERR DBE {out_dbe} BOARD '
        '[0-9]+ value out of range\r\n')
        self.assertRegex(response, f'ERR DBE {out_dbe} BOARD '
        '[0-9]+ value out of range\r\n')

    def test_setdbebpf_boardErr(self, out_dbe='SARDA_14', err_board=4):
        self._disable_board(err_board)
        message = f"DBE SETDBEBPF {out_dbe} 1\x0D\x0A"
        response = self._send(message)
        self.assertRegex(response, f'ERR DBE {out_dbe} BOARD {err_board}'
        ' unreachable\r\n')

    def test_setdbebpf_outErr(self, out_dbe='NOTHING'):
        message = f"DBE SETDBEBPF {out_dbe} 1\x0D\x0A"
        response = self._send(message)
        self.assertEqual(response, 'ERR DBE Output not existing\r\n')

    def test_setdbebpf_boardOutErr(self, out_dbe='NOTHING', err_board=4):
        self._disable_board(err_board)
        message = f"DBE SETDBEBPF {out_dbe} 1\x0D\x0A"
        response = self._send(message)
        self.assertEqual(response, 'ERR DBE Output not existing\r\n')

    def test_setdbebpf_boardValErr(self, out_dbe='SARDA_14', err_board=4):
        self._disable_board(err_board)
        message = f"DBE SETDBEBPF {out_dbe} 2\x0D\x0A"
        response = self._send(message)
        self.assertRegex(response, f'ERR DBE {out_dbe} BOARD {err_board}'
        ' value out of range\r\n')

    def test_nak_setdbebpf(self, out_dbe='1_DBBC2'):
        message = f"DBE SETDBEBPF {out_dbe}\x0D\x0A"
        response = self._send(message)
        self.assertEqual(response, 'NAK unknown command\x0D\x0A')

#       GETDBEBPF

    def test_getdbebpf_single(self, out_dbe='1_DBBC2'):
        message = f"DBE GETDBEBPF {out_dbe}\x0D\x0A"
        response = self._send(message)
        self.assertRegex(response, f'ACK {out_dbe} BOARD [0-9]+ '
        'BPF [0-9]+ VALUE [0-9]+\r\n')

    def test_getdbebpf_mult(self, out_dbe='prova'):
        message = f"DBE GETDBEBPF {out_dbe}\x0D\x0A"
        response = self._send(message)
        self.assertRegex(response, f'ACK {out_dbe} BOARD [0-9]+ '
        'BPF [0-9]+ VALUE [0-9]+\r\n')
        self.assertRegex(response, f'ACK {out_dbe} BOARD [0-9]+ '
        'BPF [0-9]+ VALUE [0-9]+\r\n')

    def test_getdbebpf_boardErr(self, out_dbe='SARDA_14', err_board=4):
        self._disable_board(err_board)
        message = f"DBE GETDBEBPF {out_dbe}\x0D\x0A"
        response = self._send(message)
        self.assertRegex(response, f'ERR DBE {out_dbe} BOARD {err_board}'
        ' unreachable\r\n')

    def test_getdbebpf_outErr(self, out_dbe='NOTHING'):
        message = f"DBE GETDBEBPF {out_dbe}\x0D\x0A"
        response = self._send(message)
        self.assertEqual(response, 'ERR DBE Output not existing\r\n')

    def test_getdbebpf_boardOutErr(self, out_dbe='NOTHING', err_board=4):
        self._disable_board(err_board)
        message = f"DBE GETDBEBPF {out_dbe}\x0D\x0A"
        response = self._send(message)
        self.assertEqual(response, 'ERR DBE Output not existing\r\n')

    def test_nak_getdbebpf(self):
        message = "DBE GETDBEBPF\x0D\x0A"
        response = self._send(message)
        self.assertEqual(response, 'NAK unknown command\x0D\x0A')


if __name__ == '__main__':
    unittest.main()
