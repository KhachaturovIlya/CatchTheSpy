
import csv
import glob
import json
import os
import sys
import zipfile
import xml.etree.ElementTree as ET
from multiprocessing import Pool

import pandas as pd

NS = '{http://schemas.openxmlformats.org/spreadsheetml/2006/main}'
CELLS = {'A5': 'flight_no', 'A9': 'date', 'C9': 'time', 'D7': 'from', 'H7': 'to'}
OUT_FIELDS = ['flight_no', 'dep_date', 'dep_time', 'from_airport', 'to_airport']

SIRENA_COLUMNS = {
    'dep_date': (72, 84),
    'dep_time': (84, 96),
    'flight_no': (120, 126),
    'dep_airport': (132, 138),
    'arr_airport': (138, 144),
}


def dmy(iso):
    y, m, d = iso.strip().split('-')
    return f'{d}.{m}.{y}'


def flight(flight_no, iso_date, frm, to):
    return flight_no.strip(), dmy(iso_date), frm.strip().upper(), to.strip().upper()


def text(el):
    return ''.join(t.text or '' for t in el.iter(NS + 't'))


def read_xlsx_file(path):
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
            flights.append((flight(rec['flight_no'], rec['date'], rec['from'], rec['to']), rec['time']))
    return flights


def read_xlsx(directory):
    files = sorted(glob.glob(os.path.join(directory, '*.xlsx')))
    with Pool() as pool:
        for file_flights in pool.imap(read_xlsx_file, files):
            yield from file_flights


def read_sirena(path):
    df = pd.read_fwf(path, colspecs=list(SIRENA_COLUMNS.values()), names=list(SIRENA_COLUMNS),
                     skiprows=1, dtype=str, keep_default_na=False)
    for r in df.itertuples(index=False):
        yield flight(r.flight_no, r.dep_date, r.dep_airport, r.arr_airport), r.dep_time


def read_pointz(path):
    for _, el in ET.iterparse(path):
        if el.tag == 'activity' and el.get('type') == 'Flight':
            yield flight(el.findtext('Code'), el.findtext('Date'),
                         el.findtext('Departure'), el.findtext('Arrival')), ''
        elif el.tag == 'user':
            el.clear()


def read_yaml(path):
    date = flight_no = None
    route = {}

    def done():
        if flight_no and route:
            return flight(flight_no, date, route.get('FROM', ''), route.get('TO', '')), ''
        return None

    for line in open(path, encoding='utf-8'):
        body = line.strip()
        if not body:
            continue
        indent = len(line) - len(line.lstrip(' '))
        if indent in (0, 2):
            if f := done():
                yield f
            route = {}
            if indent == 0:
                date, flight_no = body.strip("':"), None
            else:
                flight_no = body.rstrip(':')
        elif indent == 4:
            key, _, value = body.partition(':')
            if key in ('FROM', 'TO'):
                route[key] = value.strip()
    if f := done():
        yield f


def read_forum(path):
    for profile in json.load(open(path, encoding='utf-8'))['Forum Profiles']:
        for f in profile['Registered Flights']:
            yield flight(f['Flight'], f['Date'], f['Departure']['Airport'], f['Arrival']['Airport']), ''


def main(xlsx_dir, sirena_path, pointz_path, yaml_path, forum_path, dst):
    flights = {}
    sources = [
        ('xlsx', read_xlsx(xlsx_dir)),
        ('Sirena', read_sirena(sirena_path)),
        ('Pointz', read_pointz(pointz_path)),
        ('YAML', read_yaml(yaml_path)),
        ('форум', read_forum(forum_path)),
    ]
    for name, records in sources:
        before = len(flights)
        for key, time in records:
            if not flights.get(key):
                flights[key] = time
        print(f'{name}: новых рейсов {len(flights) - before}')

    with open(dst, 'w', encoding='utf-8', newline='') as f:
        w = csv.writer(f)
        w.writerow(OUT_FIELDS)
        for (flight_no, date, frm, to), time in flights.items():
            w.writerow([flight_no, date, time, frm, to])

    print(f'рейсов: {len(flights)}, со временем: {sum(1 for t in flights.values() if t)}')


if __name__ == '__main__':
    if len(sys.argv) != 7:
        sys.exit(__doc__)
    main(*sys.argv[1:])
