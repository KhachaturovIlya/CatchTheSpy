import csv
import json
import sys
import xml.etree.ElementTree as ET
from collections import defaultdict
from datetime import date

USAGE = ('Запуск: python quick_trips.py FrequentFlyerForum-Profiles.json PointzAggregator-AirlinesData.xml '
         'loyalty.csv passengers.csv quick_trips.csv [max_days]')
OUT_FIELDS = ['days', 'from_airport', 'to_airport', 'out_date', 'out_flight', 'back_date', 'back_flight',
              'passport', 'passport_name', 'who']

NEAR_COUNTRIES = {
    'Russian Federation', 'Russian',
    'Ukraine', 'Belarus', 'Mold', 'Kazakhstan', 'Kyrgyzstan', 'Tajikistan', 'Turkmenistan', 'Uzbekistan',
    'Armenia', 'Azerbaijan', 'Georgia', 'Estonia', 'Latvia', 'Lithuania',
    'Albania', 'Austria', 'Belgium', 'Bulgaria', 'Croatia', 'Czech Republic', 'Denmark', 'Finland', 'France',
    'Germany', 'Greece', 'Hungary', 'Iceland', 'Ireland', 'Italy', 'Luxembourg', 'Malta', 'Montenegro',
    'Netherlands', 'Norway', 'Poland', 'Portugal', 'Romania', 'Serbia', 'Slovakia', 'Slovenia',
    'Spain', 'Spain and', 'Spain and Canary', 'Spain and Canary Islands', 'Sweden', 'Switzerland', 'United Kingdom',
    'Turkey', 'Cyprus', 'Israel', 'Lebanon', 'Egypt', 'Tunisia', 'Morocco', 'Algeria',
}
NEAR_AIRPORTS = {'SKD'}  
MOSCOW_AIRPORTS = {'SVO', 'DME', 'VKO'}


def load_passports(loyalty_path, passengers_path):
    card_passports = defaultdict(set)
    with open(loyalty_path, encoding='utf-8', newline='') as f:
        for r in csv.DictReader(f):
            card_passports[f"{r['program']} {r['card_no']}"].add(r['passport'])
    names = defaultdict(list)
    with open(passengers_path, encoding='utf-8', newline='') as f:
        for r in csv.DictReader(f):
            names[r['passport']].append(f"{r['last_name']} {r['first_name']} {r['middle_name']}")
    return card_passports, {p: '; '.join(n) for p, n in names.items()}


def read_forum(path, card_passports, airports):
    people = []
    for p in json.load(open(path, encoding='utf-8'))['Forum Profiles']:
        flights = []
        for f in p['Registered Flights']:
            dep, arr = f['Departure'], f['Arrival']
            for a in (dep, arr):
                airports.setdefault(a['Airport'].upper(), (a['City'], a['Country']))
            flights.append((f['Date'], f['Flight'], dep['Airport'].upper(), arr['Airport'].upper()))
        rn = p['Real Name']
        name = f"{rn['Last Name']} {rn['First Name']}" if rn['Last Name'] else 'аноним'
        cards = {f"{l['programm']} {l['Number'].strip()}" for l in p['Loyality Programm']}
        passports = set().union(*(card_passports.get(c, set()) for c in cards))
        people.append((f"форум {p['NickName']} ({name})", passports, sorted(flights)))  # в файле не по порядку
    return people


def read_pointz(path, card_passports):
    people = []
    for _, el in ET.iterparse(path):
        if el.tag != 'user':
            continue
        n = el.find('name')
        flights, passports = [], set()
        for card in el.iter('card'):
            passports |= card_passports.get(card.get('number'), set())
            for a in card.iter('activity'):
                flights.append((a.findtext('Date'), a.findtext('Code'),
                                a.findtext('Departure').upper(), a.findtext('Arrival').upper()))
        people.append((f"Pointz {el.get('uid')} ({n.get('last')} {n.get('first')})", passports, sorted(set(flights))))
        el.clear()
    return people


def find_trips(flights, max_days, is_far):
    for a, b in zip(flights, flights[1:]):
        days = (date.fromisoformat(b[0]) - date.fromisoformat(a[0])).days
        if (a[2] == b[3] and a[3] == b[2] and 0 <= days <= max_days
                and a[2] in MOSCOW_AIRPORTS and is_far(a[3])):
            yield days, a, b


def main(forum_path, pointz_path, loyalty_path, passengers_path, dst, max_days=1):
    card_passports, passport_names = load_passports(loyalty_path, passengers_path)
    airports = {}
    people = read_forum(forum_path, card_passports, airports) + read_pointz(pointz_path, card_passports)

    def is_far(airport):
        return airport not in NEAR_AIRPORTS and airports.get(airport, ('', ''))[1] not in NEAR_COUNTRIES

    trips = {}  
    for who, passports, flights in people:
        internal = sorted(p for p in passports if len(p) == 10) or sorted(passports)
        for days, out, back in find_trips(flights, max_days, is_far):
            key = (','.join(internal) or who, out, back)
            t = trips.setdefault(key, {
                'days': days, 'from_airport': out[2], 'to_airport': out[3],
                'out_date': out[0], 'out_flight': out[1], 'back_date': back[0], 'back_flight': back[1],
                'passport': ','.join(internal),
                'passport_name': ' / '.join(passport_names.get(p, '') for p in internal),
                'who': set(),
            })
            t['who'].add(who)

    rows = sorted(trips.values(), key=lambda t: (t['to_airport'], t['out_date']))
    with open(dst, 'w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=OUT_FIELDS)
        w.writeheader()
        for t in rows:
            w.writerow({**t, 'who': '; '.join(sorted(t['who']))})

    by_dest = defaultdict(int)
    for t in rows:
        by_dest[t['to_airport']] += 1
    print(f'людей/профилей: {len(people)}, быстрых поездок из Москвы в дальние страны (до {max_days} дн.): {len(rows)}, '
          f'из них с паспортом: {sum(1 for t in rows if t["passport"])}')
    print('куда:', ', '.join(f'{a} ({airports.get(a, ("", ""))[0]}, {airports.get(a, ("", ""))[1] or "?"}): {n}'
                             for a, n in sorted(by_dest.items(), key=lambda x: -x[1])))


if __name__ == '__main__':
    if len(sys.argv) not in (6, 7):
        sys.exit(USAGE)
    main(*sys.argv[1:6], *(int(x) for x in sys.argv[6:]))
