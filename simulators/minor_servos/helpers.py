import os
import csv
import pkg_resources


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
        filename = pkg_resources.resource_filename(
            'simulators',
            'minor_servos/setup.csv'
        )
    with open(filename, 'r', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
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
                    coord = line[index].replace(';', '')
                    try:
                        if servo == 'GREGORIAN_CAP':
                            coord = int(coord)
                        else:
                            coord = float(coord)
                    except ValueError:
                        coord = None
                    coordinates.append(coord)
                configurations[line[0]][servo] = coordinates
