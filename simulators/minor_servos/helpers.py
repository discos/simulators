import os
import csv
import json
from http.server import BaseHTTPRequestHandler
from importlib.resources import files


def setup_import(servos, configurations):
    filename = os.environ.get('ACS_CDB', '/')
    filename = os.path.join(
        filename,
        'CDB',
        'alma',
        'DataBlock',
        'MinorServo',
        'Tabella Setup.csv'
    )
    if not os.path.exists(filename):
        filename = str(files('simulators') / 'minor_servos/setup.csv')
    with open(filename, 'r', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile, delimiter=';')
        indexes = {}
        for line in reader:
            if not indexes:
                for servo in servos:
                    temp = [e for e in line if e.startswith(servo)]
                    indexes[servo] = [line.index(e) for e in temp]
                continue
            for servo, servo_indexes in indexes.items():
                coordinates = []
                for index in servo_indexes:
                    coord = line[index]
                    try:
                        if servo == 'GREGORIAN_CAP':
                            coord = int(coord)
                        else:
                            coord = float(coord)
                    except ValueError:
                        coord = None
                    coordinates.append(coord)
                configurations[line[0]][servo] = coordinates


class VBrainRequestHandler(BaseHTTPRequestHandler):

    emergency = 'INAF_SRT_OR7_EMG_RESET_CMD'
    alarm = 'INAF_SRT_OR7_RESET_CMD'
    baseurl = '/Exporting/json/ExecuteCommand?name'
    urls = [
        f'{baseurl}={emergency}',
        f'{baseurl}={alarm}'
    ]
    answer = {'Message': 'OUTPUT:GOOD', 'Status': 'Good'}

    def do_GET(self):
        try:
            if self.path in self.urls:
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(self.answer).encode())
            else:
                self.send_response(404)
                self.end_headers()
        except BrokenPipeError:  # skip coverage
            pass

    def log_message(self, *_):
        pass
