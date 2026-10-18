import csv
import glob
import os
import re
import sys
import zipfile
import xml.etree.ElementTree as ET
from collections import defaultdict
from multiprocessing import Pool

NS = '{http://schemas.openxmlformats.org/spreadsheetml/2006/main}'
CELLS = {'B3': 'name', 'F3': 'card', 'A5': 'flight_no', 'A9': 'date', 'E13': 'ticket_no'}
SIRENA_DOC = (168, 180)  # позиции колонки TravelDoc в строке Sirena
OUT_FIELDS = ['program', 'card_no', 'passport']


def text(el):
    return ''.join(t.text or '' for t in el.iter(NS + 't'))


def read_file(path):
    """Талоны с картой из одного xlsx: список dict с полями из CELLS."""
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


def skeleton(word):
    """Сводит варианты транслитерации к одному виду: NATAL'YA, NATALIIA -> NATALIA; ALEKSEI, ALEXEY -> ALEXEI."""
    s = (word.upper()
             .replace("'", '')
             .replace('Y', 'I')
             .replace('TC', 'TS')
             .replace('KH', 'H')
             .replace('IE', 'E')
             .replace('KS', 'X'))
    return re.sub(r'I+', 'I', s)


def name_key(words):
    """Фамилия и имя без порядка и без инициалов: в xlsx порядок слов бывает разный."""
    return frozenset(skeleton(w) for w in words if len(w.rstrip('.')) > 1)


def load_boarding(path):
    """-> (номер билета -> паспорт, (рейс, дата, имя) -> множество паспортов)."""
    by_ticket = {}
    by_flight = defaultdict(set)
    with open(path, encoding='utf-8', newline='') as f:
        for r in csv.DictReader(f, delimiter=';'):
            passport = r['PassengerDocument'].replace(' ', '')
            if r['TicketNumber'] != 'Not presented':
                by_ticket[r['TicketNumber']] = passport
            name = name_key([r['PassengerLastName'], r['PassengerFirstName']])
            by_flight[(r['FlightNumber'], r['FlightDate'], name)].add(passport)
    return by_ticket, by_flight


def main(xlsx_dir, boarding_path, sirena_path, dst):
    cards = defaultdict(set)  # (program, card_no) -> паспорта

    # Sirena
    with open(sirena_path, encoding='utf-8') as f:
        next(f)  # заголовок
        for line in f:
            m = re.search(r'FF#([A-Z]{2}) (\d+)', line)
            if m:
                a, b = SIRENA_DOC
                cards[(m.group(1), m.group(2))].add(line[a:b].strip().replace(' ', ''))
    sirena_cards = len(cards)

    # xlsx + BoardingData.csv
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
