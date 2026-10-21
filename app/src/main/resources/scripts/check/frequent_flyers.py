import csv
import json
import sys
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict

USAGE = ('Запуск: python frequent_flyers.py FrequentFlyerForum-Profiles.json PointzAggregator-AirlinesData.xml '
         'tickets.csv loyalty.csv passengers.csv frequent_flyers.csv [top]')
OUT_FIELDS = ['passport', 'passport_name', 'flights', 'max_month', 'breaks', 'who']


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


def person_of(cards, card_passports, fallback):
    passports = set().union(*(card_passports.get(c, set()) for c in cards))
    internal = [p for p in passports if len(p) == 10]
    return internal[0] if len(internal) == 1 else fallback


def main(forum_path, pointz_path, tickets_path, loyalty_path, passengers_path, dst, top=100):
    card_passports, passport_names = load_passports(loyalty_path, passengers_path)
    flights = defaultdict(dict)
    who = defaultdict(set)

    with open(tickets_path, encoding='utf-8', newline='') as f:
        for r in csv.DictReader(f):
            d, m, y = r['dep_date'].split('.')
            flights[r['passport']][(r['flight_no'], f'{y}-{m}-{d}')] = (r['from_airport'], r['to_airport'])
            who[r['passport']].add('билеты')

    for p in json.load(open(forum_path, encoding='utf-8'))['Forum Profiles']:
        cards = {f"{l['programm']} {l['Number'].strip()}" for l in p['Loyality Programm']}
        rn = p['Real Name']
        profile = f"форум {p['NickName']} ({rn['Last Name']} {rn['First Name']})" if rn['Last Name'] \
            else f"форум {p['NickName']} (аноним)"
        person = person_of(cards, card_passports, profile)
        for f in p['Registered Flights']:
            flights[person].setdefault((f['Flight'], f['Date']),
                                       (f['Departure']['Airport'].upper(), f['Arrival']['Airport'].upper()))
        who[person].add(profile)

    for _, el in ET.iterparse(pointz_path):
        if el.tag != 'user':
            continue
        n = el.find('name')
        profile = f"Pointz {el.get('uid')} ({n.get('last')} {n.get('first')})"
        person = person_of({c.get('number') for c in el.iter('card')}, card_passports, profile)
        for a in el.iter('activity'):
            flights[person].setdefault((a.findtext('Code'), a.findtext('Date')),
                                       (a.findtext('Departure').upper(), a.findtext('Arrival').upper()))
        who[person].add(profile)
        el.clear()

    rows = []
    for person, fl in flights.items():
        trip = sorted((date, frm, to) for (_, date), (frm, to) in fl.items())
        breaks = sum(1 for a, b in zip(trip, trip[1:]) if a[2] and b[1] and a[2] != b[1])
        is_passport = person.isdigit()
        rows.append({
            'passport': person if is_passport else '',
            'passport_name': passport_names.get(person, '') if is_passport else '',
            'flights': len(fl),
            'max_month': max(Counter(date[:7] for _, date in fl).values()),
            'breaks': breaks,
            'who': '; '.join(sorted(who[person])),
        })
    rows.sort(key=lambda r: (-r['flights'], -r['breaks']))

    with open(dst, 'w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=OUT_FIELDS)
        w.writeheader()
        w.writerows(rows[:top])

    counts = sorted(r['flights'] for r in rows)
    print(f'людей: {len(rows)}, перелётов в среднем {sum(counts) / len(counts):.1f}, '
          f'у 1% больше {counts[len(counts) * 99 // 100]}, максимум {counts[-1]}')
    print(f'в топ-{top}: от {rows[min(top, len(rows)) - 1]["flights"]} перелётов, с разрывами маршрута: '
          f'{sum(1 for r in rows[:top] if r["breaks"])}')


if __name__ == '__main__':
    if len(sys.argv) not in (7, 8):
        sys.exit(USAGE)
    main(*sys.argv[1:7], *(int(x) for x in sys.argv[7:]))
