import unittest
import time
from simulators import dbesm


class TestDBESM(unittest.TestCase):

    def setUp(self):
        self.system = dbesm.System()

    def _send(self, message):
        for byte in message[:-1]:
            self.assertTrue(self.system.parse(byte))
        response = self.system.parse(message[-1])
        return response
        
    def _disable_board(self, err_board=12):
    	disable_msg = f'DBE SETSTATUS BOARD {err_board} VALUE 1\x0D\x0A'    
    	disable_response = self._send(disable_msg)

    def _test_all_boards(self, response, err_board=0):
    	for board in range(12,16):
    		if board != err_board:
    			self.assertRegex(response, f'BOARD {board} ACK')
    		else:
    			self.assertRegex(response, f'BOARD {board} ERR DBE BOARD unreachable')
    	
#       NAK


    def test_nak_generic(self):
        message = "?????\x0D\x0A"
        response = self._send(message)
        print(response)
        self.assertEqual(response, 'NAK unknown command\x0D\x0A')
        
    def test_nak_dbe_generic(self):
        message = "DBE ?????\x0D\x0A"
        response = self._send(message)
        print(response)
        self.assertEqual(response, 'NAK unknown command\x0D\x0A')
        
    def test_nak_alldiag(self):
        message = "DBE ALLDIAG ?????\x0D\x0A"
        response = self._send(message)
        print(response)
        self.assertEqual(response, 'NAK unknown command\x0D\x0A')      

    def test_nak_all_2spaces(self):
        message = "DBE SETALLMODE  MFS_7\x0D\x0A"
        response = self._send(message)
        print(response)
        self.assertEqual(response, 'NAK unknown command\x0D\x0A') 

    def test_nak_set_2spaces(self, ch=0, board=15, val=0.0):
        message = f"DBE SETATT  {ch} BOARD {board} VALUE {val}\x0D\x0A"
        response = self._send(message)
        print(response)
        self.assertEqual(response, 'NAK unknown command\x0D\x0A')
        
    def test_nak_set_3spaces(self, ch=0, board=15, val=0.0):
        message = f"DBE SETATT   {ch} BOARD {board} VALUE {val}\x0D\x0A"
        response = self._send(message)
        print(response)
        self.assertEqual(response, 'NAK unknown command\x0D\x0A')    
        
    def test_nak_set_space_end(self, ch=0, board=15, val=0.0):
        message = f"DBE SETATT {ch} BOARD {board} VALUE {val} \x0D\x0A"
        response = self._send(message)
        print(response)
        self.assertEqual(response, 'NAK unknown command\x0D\x0A')    
        
    def test_nak_set_2spaces_end(self, ch=0, board=15, val=0.0):
        message = f"DBE SETATT {ch} BOARD {board} VALUE {val}  \x0D\x0A"
        response = self._send(message)
        print(response)
        self.assertEqual(response, 'NAK unknown command\x0D\x0A')    

    def test_nak_set_3spaces_end(self, ch=0, board=15, val=0.0):
        message = f"DBE SETATT {ch} BOARD {board} VALUE {val}   \x0D\x0A"
        response = self._send(message)
        print(response)
        self.assertEqual(response, 'NAK unknown command\x0D\x0A') 


#       ALLDIAG, CLRMODE


    def test_all_diag_ok(self):
        message = "DBE ALLDIAG\x0D\x0A"
        response = self._send(message)
        print(response)
        # self.assertEqual(len(response), 1)
        # self.assertEqual(response[0], 'ack')
        self._test_all_boards(response)
        
    def test_all_diag_boardErr(self, err_board=12):
        message = "DBE ALLDIAG\x0D\x0A"
        self._disable_board(err_board)
        response = self._send(message)
        print(response)
        self._test_all_boards(response, err_board)     

    
    def test_clrmode_ok(self, obs_mode='CustomCfg'):
        message1 = f"DBE STOREALLMODE {obs_mode}\x0D\x0A"
        response1 = self._send(message1)
        message = f"DBE CLRMODE {obs_mode}\x0D\x0A"
        response = self._send(message)
        print(response)
        self.assertEqual(response, 'ACK\x0D\x0A')
        
    def test_clrmode_err(self, obs_mode='CustomCfg'):
        message = f"DBE CLRMODE {obs_mode}\x0D\x0A"
        response = self._send(message)
        print(response)
        self.assertEqual(response, 'ERR DBE CFG file not existing\x0D\x0A')    
        

#       SETALLMODE, STOREALLMODE


    def test_setallmode_ok(self, obs_mode='MFS_7'):
        message = f"DBE SETALLMODE {obs_mode}\x0D\x0A"
        response = self._send(message)
        print(response)
        self._test_all_boards(response)
        
    def test_setallmode_boardErr(self, obs_mode='MFS_7', err_board=12):
        message = f"DBE SETALLMODE {obs_mode}\x0D\x0A"
        self._disable_board(err_board)
        response = self._send(message)
        print(response)
        self._test_all_boards(response, err_board)
        
    def test_setallmode_cfgErr(self, obs_mode='PIPPO'):
        message = f"DBE SETALLMODE {obs_mode}\x0D\x0A"
        response = self._send(message)
        print(response)
        self.assertEqual(response, 'ERR DBE CFG file not existing\x0D\x0A')   
        
    def test_setallmode_bothErr(self, obs_mode='PIPPO', err_board=12):
        message = f"DBE SETALLMODE {obs_mode}\x0D\x0A"
        self._disable_board(err_board)
        response = self._send(message)
        print(response)
        self.assertEqual(response, 'ERR DBE CFG file not existing\x0D\x0A') 
        

    def test_storeallmode_ok(self, obs_mode='CustomCfg'):
        message = f"DBE STOREALLMODE {obs_mode}\x0D\x0A"
        response = self._send(message)
        print(response)
        self.assertEqual(response, 'ACK\x0D\x0A')     
        
    def test_storeallmode_boardErr(self, obs_mode='CustomCfg', err_board=12):
        message = f"DBE STOREALLMODE {obs_mode}\x0D\x0A"
        self._disable_board(err_board)
        response = self._send(message)
        print(response)
        self.assertEqual(response, f'ERR DBE BOARD {err_board} unreachable\x0D\x0A')     
        
    def test_storeallmode_2boardErr(self, obs_mode='CustomCfg', err_board1=12, err_board2=13):
        message = f"DBE STOREALLMODE {obs_mode}\x0D\x0A"
        self._disable_board(err_board1)
        self._disable_board(err_board2)
        response = self._send(message)
        print(response)
        self.assertEqual(response, f'ERR DBE BOARD {err_board1} {err_board2} unreachable\x0D\x0A')    
        
    def test_storeallmode_cfgErr(self, obs_mode='MFS_7'):
        message = f"DBE STOREALLMODE {obs_mode}\x0D\x0A"
        response = self._send(message)
        print(response)
        self.assertEqual(response, 'ERR DBE writing cfg file\x0D\x0A')
        
    def test_storeallmode_bothErr(self, obs_mode='MFS_7', err_board=12):
        message = f"DBE STOREALLMODE {obs_mode}\x0D\x0A"
        self._disable_board(err_board)
        response = self._send(message)
        print(response)
        self.assertEqual(response, 'ERR DBE writing cfg file\x0D\x0A')     
        
          
#      MODE


    def test_mode_ok(self, board=15, obs_mode='MFS_7'):
        message = f"DBE MODE BOARD {board} {obs_mode}\x0D\x0A"
        response = self._send(message)
        print(response)
        self.assertEqual(response, 'ACK\x0D\x0A')        
        
    def test_mode_boardErr(self, board=15, obs_mode='MFS_7'):
        message = f"DBE MODE BOARD {board} {obs_mode}\x0D\x0A"
        self._disable_board(board)
        response = self._send(message)
        print(response)
        self.assertEqual(response, f'ERR DBE BOARD {board} unreachable\x0D\x0A')     
        
    def test_mode_cfgErr(self, board=15, obs_mode='PIPPO'):
        message = f"DBE MODE BOARD {board} {obs_mode}\x0D\x0A"
        response = self._send(message)
        print(response)
        self.assertEqual(response, 'ERR DBE CFG file not existing\x0D\x0A')  
        
    def test_mode_bothErr(self, board=15, obs_mode='PIPPO'):
        message = f"DBE MODE BOARD {board} {obs_mode}\x0D\x0A"
        self._disable_board(board)
        response = self._send(message)
        print(response)
        self.assertEqual(response, 'ERR DBE CFG file not existing\x0D\x0A')      
        
        
#      DIAG, GETSTATUS, GETCOMP        
    
    
    def test_diag_ok(self, board=15):
        message = f"DBE DIAG BOARD {board}\x0D\x0A"
        response = self._send(message)
        print(response)
        self.assertRegex(response, f'ACK\nBOARD {board}')    
    
    def test_diag_boardErr(self, board=15):
        message = f"DBE DIAG BOARD {board}\x0D\x0A"
        self._disable_board(board)
        response = self._send(message)
        print(response)
        self.assertEqual(response, f'ERR DBE BOARD {board} unreachable\x0D\x0A')
        
        
    def test_getstatus_ok(self, board=15):
        message = f"DBE GETSTATUS BOARD {board}\x0D\x0A"
        response = self._send(message)
        print(response)
        self.assertRegex(response, f'ACK\nBOARD {board}\n\nREG=')
        self.assertRegex(response, ' ]\n\nATT=')
        self.assertRegex(response, ' ]\r\n') 
    
    def test_getstatus_boardErr(self, board=15):
        message = f"DBE GETSTATUS BOARD {board}\x0D\x0A"
        self._disable_board(board)
        response = self._send(message)
        print(response)
        self.assertEqual(response, f'ERR DBE BOARD {board} unreachable\x0D\x0A')
        
        
    def test_getcomp_ok(self, board=15):
        message = f"DBE GETCOMP BOARD {board}\x0D\x0A"
        response = self._send(message)
        print(response)
        self.assertRegex(response, f'ACK\nBOARD {board}\n\nAMP=')
        self.assertRegex(response, ']\nEQ=')   
        self.assertRegex(response, ']\nBPF=') 
        self.assertRegex(response, ']\r\n')
    
    def test_getcomp_boardErr(self, board=15):
        message = f"DBE GETCOMP BOARD {board}\x0D\x0A"
        self._disable_board(board)
        response = self._send(message)
        print(response)
        self.assertEqual(response, f'ERR DBE BOARD {board} unreachable\x0D\x0A')
          
        
#      SETATT


    def test_setatt_ok(self, ch=0, board=15, val=0.0):
        message = f"DBE SETATT {ch} BOARD {board} VALUE {val}\x0D\x0A"
        response = self._send(message)
        print(response)
        self.assertEqual(response, 'ACK\x0D\x0A')        
        
    def test_setatt_chErr1(self, ch=18, board=15, val=0.0):
        message = f"DBE SETATT {ch} BOARD {board} VALUE {val}\x0D\x0A"
        response = self._send(message)
        print(response)
        self.assertEqual(response, f'ERR DBE ATT {ch} not existing\x0D\x0A')     
        
    def test_setatt_chErr2(self, ch=0.0, board=15, val=0.0):
        message = f"DBE SETATT {ch} BOARD {board} VALUE {val}\x0D\x0A"
        response = self._send(message)
        print(response)
        self.assertEqual(response, 'NAK unknown command\x0D\x0A')
        
    def test_setatt_boardErr(self, ch=0, board=15, val=0.0):
        message = f"DBE SETATT {ch} BOARD {board} VALUE {val}\x0D\x0A"
        self._disable_board(board)
        response = self._send(message)
        print(response)
        self.assertEqual(response, f'ERR DBE BOARD {board} unreachable\x0D\x0A')
        
    def test_setatt_valErr1(self, ch=0, board=15, val=0.6):
        message = f"DBE SETATT {ch} BOARD {board} VALUE {val}\x0D\x0A"
        response = self._send(message)
        print(response)
        self.assertEqual(response, 'ERR DBE value out of range\x0D\x0A')     
        
    def test_setatt_valErr2(self, ch=0, board=15, val=32.0):
        message = f"DBE SETATT {ch} BOARD {board} VALUE {val}\x0D\x0A"
        response = self._send(message)
        print(response)
        self.assertEqual(response, 'ERR DBE value out of range\x0D\x0A')
        
    def test_setatt_twoErr(self, ch=18, board=15, val=0.6):
        message = f"DBE SETATT {ch} BOARD {board} VALUE {val}\x0D\x0A"
        response = self._send(message)
        print(response)
        self.assertEqual(response, f'ERR DBE ATT {ch} not existing\x0D\x0A')          
        
    def test_setatt_threeErr(self, ch=18, board=15, val=0.6):
        message = f"DBE SETATT {ch} BOARD {board} VALUE {val}\x0D\x0A"
        self._disable_board(board)
        response = self._send(message)
        print(response)
        self.assertEqual(response, f'ERR DBE BOARD {board} unreachable\x0D\x0A')    
         

#      SETAMP


    def test_setamp_ok(self, ch=1, board=15, val=0):
        message = f"DBE SETAMP {ch} BOARD {board} VALUE {val}\x0D\x0A"
        response = self._send(message)
        print(response)
        self.assertEqual(response, 'ACK\x0D\x0A')        
        
    def test_setamp_chErr1(self, ch=11, board=15, val=0):
        message = f"DBE SETAMP {ch} BOARD {board} VALUE {val}\x0D\x0A"
        response = self._send(message)
        print(response)
        self.assertEqual(response, f'ERR DBE AMP {ch} not existing\x0D\x0A')     
        
    def test_setamp_chErr2(self, ch=1.0, board=15, val=0):
        message = f"DBE SETAMP {ch} BOARD {board} VALUE {val}\x0D\x0A"
        response = self._send(message)
        print(response)
        self.assertEqual(response, 'NAK unknown command\x0D\x0A')
        
    def test_setamp_boardErr(self, ch=1, board=15, val=0):
        message = f"DBE SETAMP {ch} BOARD {board} VALUE {val}\x0D\x0A"
        self._disable_board(board)
        response = self._send(message)
        print(response)
        self.assertEqual(response, f'ERR DBE BOARD {board} unreachable\x0D\x0A')
        
    def test_setamp_valErr1(self, ch=1, board=15, val=0.6):
        message = f"DBE SETAMP {ch} BOARD {board} VALUE {val}\x0D\x0A"
        response = self._send(message)
        print(response)
        self.assertEqual(response, 'ERR DBE value out of range\x0D\x0A')     
        
    def test_setamp_valErr2(self, ch=1, board=15, val=2):
        message = f"DBE SETAMP {ch} BOARD {board} VALUE {val}\x0D\x0A"
        response = self._send(message)
        print(response)
        self.assertEqual(response, 'ERR DBE value out of range\x0D\x0A')
        
    def test_setamp_twoErr(self, ch=11, board=15, val=2):
        message = f"DBE SETAMP {ch} BOARD {board} VALUE {val}\x0D\x0A"
        response = self._send(message)
        print(response)
        self.assertEqual(response, f'ERR DBE AMP {ch} not existing\x0D\x0A')          
        
    def test_setamp_threeErr(self, ch=11, board=15, val=2):
        message = f"DBE SETAMP {ch} BOARD {board} VALUE {val}\x0D\x0A"
        self._disable_board(board)
        response = self._send(message)
        print(response)
        self.assertEqual(response, f'ERR DBE BOARD {board} unreachable\x0D\x0A')
        
        
#      SETEQ


    def test_seteq_ok(self, ch=1, board=15, val=0):
        message = f"DBE SETEQ {ch} BOARD {board} VALUE {val}\x0D\x0A"
        response = self._send(message)
        print(response)
        self.assertEqual(response, 'ACK\x0D\x0A')        
        
    def test_seteq_chErr1(self, ch=11, board=15, val=0):
        message = f"DBE SETEQ {ch} BOARD {board} VALUE {val}\x0D\x0A"
        response = self._send(message)
        print(response)
        self.assertEqual(response, f'ERR DBE EQ {ch} not existing\x0D\x0A')     
        
    def test_seteq_chErr2(self, ch=1.0, board=15, val=0):
        message = f"DBE SETEQ {ch} BOARD {board} VALUE {val}\x0D\x0A"
        response = self._send(message)
        print(response)
        self.assertEqual(response, 'NAK unknown command\x0D\x0A')
        
    def test_seteq_boardErr(self, ch=1, board=15, val=0):
        message = f"DBE SETEQ {ch} BOARD {board} VALUE {val}\x0D\x0A"
        self._disable_board(board)
        response = self._send(message)
        print(response)
        self.assertEqual(response, f'ERR DBE BOARD {board} unreachable\x0D\x0A')
        
    def test_seteq_valErr1(self, ch=1, board=15, val=0.6):
        message = f"DBE SETEQ {ch} BOARD {board} VALUE {val}\x0D\x0A"
        response = self._send(message)
        print(response)
        self.assertEqual(response, 'ERR DBE value out of range\x0D\x0A')     
        
    def test_seteq_valErr2(self, ch=1, board=15, val=2):
        message = f"DBE SETEQ {ch} BOARD {board} VALUE {val}\x0D\x0A"
        response = self._send(message)
        print(response)
        self.assertEqual(response, 'ERR DBE value out of range\x0D\x0A')
        
    def test_seteq_twoErr(self, ch=11, board=15, val=2):
        message = f"DBE SETEQ {ch} BOARD {board} VALUE {val}\x0D\x0A"
        response = self._send(message)
        print(response)
        self.assertEqual(response, f'ERR DBE EQ {ch} not existing\x0D\x0A')          
        
    def test_seteq_threeErr(self, ch=11, board=15, val=2):
        message = f"DBE SETEQ {ch} BOARD {board} VALUE {val}\x0D\x0A"
        self._disable_board(board)
        response = self._send(message)
        print(response)
        self.assertEqual(response, f'ERR DBE BOARD {board} unreachable\x0D\x0A')
        
#      SETBPF


    def test_setbpf_ok(self, ch='1a', board=15, val=0):
        message = f"DBE SETBPF {ch} BOARD {board} VALUE {val}\x0D\x0A"
        response = self._send(message)
        print(response)
        self.assertEqual(response, 'ACK\x0D\x0A')        
        
    def test_setbpf_chErr1(self, ch=11, board=15, val=0):
        message = f"DBE SETBPF {ch} BOARD {board} VALUE {val}\x0D\x0A"
        response = self._send(message)
        print(response)
        self.assertEqual(response, f'ERR DBE BPF {ch} not existing\x0D\x0A')     
        
    def test_setbpf_chErr2(self, ch='1.a', board=15, val=0):
        message = f"DBE SETBPF {ch} BOARD {board} VALUE {val}\x0D\x0A"
        response = self._send(message)
        print(response)
        self.assertEqual(response, f'ERR DBE BPF {ch} not existing\x0D\x0A')
        
    def test_setbpf_boardErr(self, ch='1a', board=15, val=0):
        message = f"DBE SETBPF {ch} BOARD {board} VALUE {val}\x0D\x0A"
        self._disable_board(board)
        response = self._send(message)
        print(response)
        self.assertEqual(response, f'ERR DBE BOARD {board} unreachable\x0D\x0A')
        
    def test_setbpf_valErr1(self, ch='1a', board=15, val=0.6):
        message = f"DBE SETBPF {ch} BOARD {board} VALUE {val}\x0D\x0A"
        response = self._send(message)
        print(response)
        self.assertEqual(response, 'ERR DBE value out of range\x0D\x0A')     
        
    def test_setbpf_valErr2(self, ch='1a', board=15, val=2):
        message = f"DBE SETBPF {ch} BOARD {board} VALUE {val}\x0D\x0A"
        response = self._send(message)
        print(response)
        self.assertEqual(response, 'ERR DBE value out of range\x0D\x0A')
        
    def test_setbpf_twoErr(self, ch=11, board=15, val=2):
        message = f"DBE SETBPF {ch} BOARD {board} VALUE {val}\x0D\x0A"
        response = self._send(message)
        print(response)
        self.assertEqual(response, f'ERR DBE BPF {ch} not existing\x0D\x0A')          
        
    def test_setbpf_threeErr(self, ch=11, board=15, val=2):
        message = f"DBE SETBPF {ch} BOARD {board} VALUE {val}\x0D\x0A"
        self._disable_board(board)
        response = self._send(message)
        print(response)
        self.assertEqual(response, f'ERR DBE BOARD {board} unreachable\x0D\x0A')              
              
if __name__ == '__main__':
    unittest.main()
