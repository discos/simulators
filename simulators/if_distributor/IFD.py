from simulators.common import ListeningSystem


class System(ListeningSystem):
    """The IFDistributor, also known as Intermediate Frequency Distributor,
    shifts the received signal wave by means of a local oscillator.
    This system is the simulator of the SRT LP band IFDistributor."""

    tail = ['\x0A', '\x0D']  # NEWLINE and CR
    ref_freq = 10
    ol_freq = 2300
    max_attenuation = 31.5
    max_msg_length = 15  # 'S 0 100 2300 1\n'

    ack = 'ack\n'
    nak = 'nak\n'

    commands = {
        '?': '_get_status',
        'B': '_set_bandwidth',
        'S': '_set_lo',
        'A': '_set_att',
        'I': '_set_input'
    }

    def __init__(self):
        self.boards = {}

        self.boards[0] = self._init_board(0, 2)
        self.boards[1] = self._init_board(1, 0)
        self.boards[2] = self._init_board(2, 1)
        self.boards[3] = self._init_board(3, 3)
        self.boards[4] = self._init_board(4, 4)
        for i in range(5, 21):
            self.boards[i] = self._init_board(i, 5)

        self.msg = ''

    def _init_board(self, address, pcb_type):
        """This method initializes the status of a given board.

        :param address: the address of the board to initialize.
        :param pcb_type: the type of the board to initialize.
        """
        board_status = [
            address,
            address,
            pcb_type,
            self.ref_freq,
            0,
            255,
            255,
            255,
            255,
            0,
            1,
            0
        ]

        if pcb_type in range(2):
            board_status[3] = board_status[4] = 65535
            board_status[10] = board_status[11] = -1

        if pcb_type == 1:
            board_status[9] = int('00000010', 2)

        if pcb_type in range(2, 6):
            board_status[4] = self.ol_freq
            board_status[10] = 1

        if pcb_type == 5:
            board_status[5:9] = 4 * [63]

        return board_status

    def parse(self, byte):
        self.msg += byte

        if len(self.msg) == 1:
            if byte in self.commands.keys():
                return True
            else:
                self.msg = ''
                return False
        elif len(self.msg) < self.max_msg_length:
            if byte not in self.tail:
                return True
        elif len(self.msg) == self.max_msg_length:
            if byte not in self.tail:
                self.msg = ''
                raise ValueError(
                    'Message too long: max length should be %d'
                    % self.max_msg_length
                )

        msg = self.msg[:-1]
        self.msg = ''
        return self._execute(msg)

    def _execute(self, msg):
        """This method parses and executes a command the moment it is
        completely received.

        :param msg: the received command, comprehensive of its header and tail.
        """
        if len(msg) < 3:
            raise ValueError('Message too short.')

        args = [x.strip() for x in msg.split(' ')]

        if len(args) < 2:
            raise ValueError('Too few arguments.')

        cmd = self.commands.get(args[0])
        if not cmd:
            return self.nak
        cmd = getattr(self, cmd)

        args = args[1:]

        params = []
        try:
            for param in args:
                if '.' in param:
                    params.append(float(param))
                else:
                    params.append(int(param))
        except ValueError:
            raise ValueError(
                'Wrong argument format. '
                + 'Use only integers or floating point numbers.'
            )

        if params[0] not in range(len(self.boards)):
            raise IndexError(
                'Please, specify a board slot in range [0:%d].'
                % len(self.boards)
            )

        return cmd(params)

    def _get_status(self, params):
        """This method retrieves the status of the given board.

        :param params: one accepted parameter, which is the index of the
            desired board.
        """
        if len(params) != 1:
            raise ValueError('Wrong number of arguments for command `?`.')

        response = (
            self.ack
            + ', '.join([str(x) for x in self.boards[params[0]]])
            + '\n'
        )

        return response

    def _set_bandwidth(self, params):
        """This method sets the bandwidth on type 0 and 1 boards.

        :param params: two accepted parameters, the first one is the board
            index, the second one is the desired bandwidth, 0 for a narrow
            filter, 1 for a medium, 2 for a large and 3 for no filter at all.
        """
        if len(params) != 2:
            raise ValueError('Wrong number of arguments for command `B`.')
        if params[1] not in range(4):
            raise ValueError(
                'Wrong bandwidth for command `B`. Please, use [0:3].'
            )

        status = self.boards[params[0]]

        if status[2] not in [0, 1]:
            return self.nak

        sr = bin(status[9])[2:].zfill(8)
        status[9] = int(
            (
                sr[0:3]
                + bin(params[1])[2:].zfill(2)
                + sr[5:]
            ),
            2
        )
        self.boards[params[0]] = status
        return self.ack

    def _set_lo(self, params):
        """This method handles the local oscillator on type 2 boards.

        :param params: four accepted parameters, the first one is the board
            index, the second one is the reference frequency, the third one
            is the local oscillator frequency, the fourth one can be 0 or 1,
            indicating whether the local oscillator should be enabled (1) or
            disabled (0).
        """
        if len(params) != 4:
            raise ValueError('Wrong number of arguments for command `S`.')
        if params[1] != self.ref_freq:
            raise ValueError(
                'Wrong reference frequency. Please, use %d.' % self.ref_freq)
        if params[3] not in [0, 1]:
            raise ValueError(
                'Wrong enable parameter for command `S`. Please, use 0 or 1.'
            )

        status = self.boards[params[0]]

        if status[2] != 2:
            return self.nak

        status[3] = params[1]
        status[4] = params[2]
        sr = bin(status[9])[2:].zfill(8)
        status[9] = int(
            (
                sr[0:4]
                + str(params[3])
                + sr[5:]
            ),
            2
        )
        status[10] = params[3] ^ 1
        status[11] = params[3]
        self.boards[params[0]] = status
        return self.ack

    def _set_att(self, params):
        """This method sets the attenuation to type 5 boards.

        :param params: three accepted parameters, the first one is the board
            index, the second one is the channel to which the command will sets
            the attenuation (range 0 to 3), the third one
            is the attenuation value (range 0 to 31.5dB)
        """
        if len(params) != 3:
            raise ValueError('Wrong number of arguments for command `A`.')
        if params[1] not in range(4):
            raise IndexError(
                'Wrong channel number for command `A`. Please, use [0:3].'
            )
        if params[2] < 0 or params[2] > self.max_attenuation:
            return self.nak

        status = self.boards[params[0]]

        if status[2] != 5:
            return self.nak

        status[5 + params[1]] = int(params[2] * 2)
        self.boards[params[0]] = status
        return self.ack

    def _set_input(self, params):
        """This method sets the input conversion on type 1 boards.

        :param params: two accepted parameters, the first one is the board
            index, the second one is a boolean indicating whether the RF input
            signal should be converted
        """
        if len(params) != 2:
            raise ValueError('Wrong number of arguments for command `I`.')
        if params[1] not in [0, 1]:
            raise ValueError(
                'Wrong parameter for command `I`. Please, use 0 or 1.'
            )

        status = self.boards[params[0]]

        if status[2] != 1:
            return self.nak

        sr = bin(status[9])[2:].zfill(8)
        status[9] = int(
            (
                sr[0:5]
                + bin(params[1] + 1)[2:].zfill(2)
                + sr[7]
            ),
            2
        )
        self.boards[params[0]] = status
        return self.ack
