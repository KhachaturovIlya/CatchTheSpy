# Запуск: python3 boarding_flights.py {путь до входного .csv файла} {путь до итогового файла}

import csv
import glob
import os
import sys
import zipfile
import xml.etree.ElementTree as ET
from datetime import datetime
from multiprocessing import Pool

NS = '{http://schemas.openxmlformats.org/spreadsheetml/2006/main}'
CELLS = {'A5': 'flight_no', 'A9': 'date', 'C9': 'time', 'D7': 'from', 'H7': 'to'}
OUT_FIELDS = ['flight_no', 'dep_date', 'dep_time', 'from_airport', 'to_airport']


def text(el):
    return ''.join(t.text or '' for t in el.iter(NS + 't'))


def read_file(path):
    """Рейсы со всех листов одного xlsx: список (flight_no, date, time, from, to)."""
    flights = []
    with zipfile.ZipFile(path) as z:
        names = z.namelist()
        shared = []
        if 'xl/sharedStrings.xml' in names:
            shared = [text(si) for si in ET.fromstring(z.read('xl/sharedStrings.xml')).iter(NS + 'si')]

        for name in names:
            if not (name.startswith('xl/worksheets/sheet') and name.endswith('.xml')):
                continue
            rec = {}
            for c in ET.fromstring(z.read(name)).iter(NS + 'c'):
                field = CELLS.get(c.get('r'))
                if field is None:
                    continue
                if c.get('t') == 'inlineStr':
                    rec[field] = text(c).strip()
                elif (v := c.find(NS + 'v')) is not None:
                    rec[field] = (shared[int(v.text)] if c.get('t') == 's' else v.text).strip()
            flights.append((
                rec['flight_no'],
                datetime.strptime(rec['date'], '%Y-%m-%d').strftime('%d.%m.%Y'),
                rec['time'],
                rec['from'],
                rec['to'],
            ))
    return flights


def main(src_dir, dst):
    files = sorted(glob.glob(os.path.join(src_dir, '*.xlsx')))
    flights = {}  # (flight_no, date, from, to) -> time
    passes = 0
    with Pool() as pool:
        for file_flights in pool.imap(read_file, files):
            for flight_no, date, time, frm, to in file_flights:
                flights.setdefault((flight_no, date, frm, to), time)
                passes += 1

    with open(dst, 'w', encoding='utf-8', newline='') as f:
        w = csv.writer(f)
        w.writerow(OUT_FIELDS)
        for (flight_no, date, frm, to), time in flights.items():
            w.writerow([flight_no, date, time, frm, to])

    print(f'файлов: {len(files)}, талонов: {passes}, рейсов: {len(flights)}')


if __name__ == '__main__':
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])
