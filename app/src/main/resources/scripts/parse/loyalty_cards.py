import csv
import glob
import os
import re
import sys
import zipfile
import xml.etree.ElementTree as ET
from collections import defaultdict
from multiprocessing import Pool

import pandas as pd

NS = '{http://schemas.openxmlformats.org/spreadsheetml/2006/main}'
CELLS = {'B3': 'name', 'F3': 'card', 'A5': 'flight_no', 'A9': 'date', 'E13': 'ticket_no'}
SIRENA_COLUMNS = {
    'doc': (168, 180),
    'add_info': (240, 276),
}
OUT_FIELDS = ['program', 'card_no', 'passport']


def text(el):
    return ''.join(t.text or '' for t in el.iter(NS + 't'))


def read_file(path):
    passes = []
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
            if rec.get('card'):
                passes.append(rec)
    return passes

# (program, card_no) -> паспорта
def skeleton(word):
    s = (word.upper()
             .replace("'", '')
             .replace('Y', 'I')
             .replace('TC', 'TS')
             .replace('KH', 'H')
             .replace('IE', 'E')
             .replace('KS', 'X'))
    return re.sub(r'I+', 'I', s)


def name_key(words):
    return frozenset(skeleton(w) for w in words if len(w.rstrip('.')) > 1)


def load_boarding(path):
    df = pd.read_csv(path, sep=';', dtype=str, keep_default_na=False)
    df['passport'] = df['PassengerDocument'].str.replace(' ', '')
    with_ticket = df[df['TicketNumber'] != 'Not presented']
    by_ticket = dict(zip(with_ticket['TicketNumber'], with_ticket['passport']))
    by_flight = defaultdict(set)
    for r in df.itertuples(index=False):
        by_flight[(r.FlightNumber, r.FlightDate, name_key([r.PassengerLastName, r.PassengerFirstName]))].add(r.passport)
    return by_ticket, by_flight


def read_sirena_cards(path):
    df = pd.read_fwf(path, colspecs=list(SIRENA_COLUMNS.values()), names=list(SIRENA_COLUMNS),
                     skiprows=1, dtype=str, keep_default_na=False)
    cards = df['add_info'].str.extract(r'FF#([A-Z]{2}) (\d+)')
    cards.columns = ['program', 'card_no']
    cards['passport'] = df['doc'].str.replace(' ', '')
    return cards.dropna()


def main(xlsx_dir, boarding_path, sirena_path, dst):
    cards = defaultdict(set)

    for r in read_sirena_cards(sirena_path).itertuples(index=False):
        cards[(r.program, r.card_no)].add(r.passport)
    sirena_cards = len(cards)

    by_ticket, by_flight = load_boarding(boarding_path)
    files = sorted(glob.glob(os.path.join(xlsx_dir, '*.xlsx')))
    with Pool() as pool:
        for passes in pool.imap(read_file, files):
            for p in passes:
                program, card_no = p['card'].split()
                passport = by_ticket.get(p['ticket_no'])
                if passport is None:
                    found = by_flight.get((p['flight_no'], p['date'], name_key(p['name'].split())), set())
                    passport = next(iter(found)) if len(found) == 1 else None
                if passport:
                    cards[(program, card_no)].add(passport)

    rows = 0
    with open(dst, 'w', encoding='utf-8', newline='') as f:
        w = csv.writer(f)
        w.writerow(OUT_FIELDS)
        for (program, card_no), passports in cards.items():
            for passport in sorted(passports):
                w.writerow([program, card_no, passport])
                rows += 1

    print(f'карт: {len(cards)} (из них в Sirena {sirena_cards}), строк: {rows}')


if __name__ == '__main__':
    if len(sys.argv) != 5:
        sys.exit(__doc__)
    main(*sys.argv[1:])
