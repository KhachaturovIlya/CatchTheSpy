import csv
import re
import sys
import xml.etree.ElementTree as ET
from collections import defaultdict

OUT_FIELDS = ['program', 'card_no', 'source', 'last_name', 'first_name', 'passport']


def skeleton(word):
    s = (word.upper()
             .replace("'", '')
             .replace('Y', 'I')
             .replace('TC', 'TS')
             .replace('KH', 'H')
             .replace('IE', 'E')
             .replace('KS', 'X'))
    return re.sub(r'I+', 'I', s)


def person(last, first):
    return skeleton(last), skeleton(first)


def main(pointz_path, loyalty_path, passengers_path, dst):
    people = defaultdict(dict)

    for _, el in ET.iterparse(pointz_path):
        if el.tag != 'user':
            continue
        name = el.find('name')
        last, first = name.get('last'), name.get('first')
        for card in el.iter('card'):
            program, card_no = card.get('number').split()
            people[(program, card_no)].setdefault(person(last, first), {
                'source': 'Pointz', 'last_name': last, 'first_name': first, 'passport': ''})
        el.clear()

    names = defaultdict(list)
    with open(passengers_path, encoding='utf-8', newline='') as f:
        for r in csv.DictReader(f):
            names[r['passport']].append((r['last_name'], r['first_name']))
    with open(loyalty_path, encoding='utf-8', newline='') as f:
        for r in csv.DictReader(f):
            for last, first in names.get(r['passport'], []):
                p = people[(r['program'], r['card_no'])].setdefault(person(last, first), {
                    'source': 'loyalty', 'last_name': last, 'first_name': first, 'passport': ''})
                p['passport'] = r['passport']
                if p['source'] == 'Pointz':
                    p['source'] = 'Pointz+loyalty'

    shared = {card: by_person for card, by_person in people.items() if len(by_person) > 1}

    with open(dst, 'w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=OUT_FIELDS)
        w.writeheader()
        for (program, card_no), by_person in shared.items():
            for p in by_person.values():
                w.writerow({'program': program, 'card_no': card_no, **p})

    print(f'карт: {len(people)}, из них у нескольких людей: {len(shared)}')
    for (program, card_no), by_person in shared.items():
        who = '; '.join(f"{p['last_name']} {p['first_name']} {p['passport']} ({p['source']})".replace('  ', ' ')
                        for p in by_person.values())
        print(f'  {program} {card_no}: {who}')


if __name__ == '__main__':
    if len(sys.argv) != 5:
        sys.exit(__doc__)
    main(*sys.argv[1:])
