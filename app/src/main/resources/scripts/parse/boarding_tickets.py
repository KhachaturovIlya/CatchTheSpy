import csv
import sys
from collections import Counter, defaultdict

import pandas as pd

OUT_FIELDS = ['passport', 'flight_no', 'dep_date', 'ticket_no', 'from_airport', 'to_airport']

SIRENA_COLUMNS = {
    'name': (0, 60),
    'dep_date': (72, 84),
    'flight_no': (120, 126),
    'dep_airport': (132, 138),
    'arr_airport': (138, 144),
    'ticket_no': (150, 168),
    'doc': (168, 180),
}

ICAO = {
    'А': 'A', 'Б': 'B', 'В': 'V', 'Г': 'G', 'Д': 'D', 'Е': 'E', 'Ё': 'E', 'Ж': 'ZH', 'З': 'Z',
    'И': 'I', 'Й': 'I', 'К': 'K', 'Л': 'L', 'М': 'M', 'Н': 'N', 'О': 'O', 'П': 'P', 'Р': 'R',
    'С': 'S', 'Т': 'T', 'У': 'U', 'Ф': 'F', 'Х': 'KH', 'Ц': 'TS', 'Ч': 'CH', 'Ш': 'SH',
    'Щ': 'SHCH', 'Ъ': 'IE', 'Ы': 'Y', 'Ь': '', 'Э': 'E', 'Ю': 'IU', 'Я': 'IA',
}


def translit(word):
    return ''.join(ICAO.get(ch, ch) for ch in word.upper())


def dmy(iso):
    y, m, d = iso.strip().split('-')
    return f'{d}.{m}.{y}'


def load_flights(path):
    flights = defaultdict(list)
    with open(path, encoding='utf-8', newline='') as f:
        for r in csv.DictReader(f):
            flights[(r['flight_no'], r['dep_date'])].append((r['dep_time'], r['from_airport'], r['to_airport']))
    return flights


def find_route(candidates, time, to_airport):
    if to_airport:
        candidates = [c for c in candidates if c[2] == to_airport]
    same_time = [c for c in candidates if c[0] == time]
    no_time = [c for c in candidates if not c[0]]
    if len(same_time) == 1:
        return same_time[0][1], same_time[0][2]
    if not same_time and len(no_time) == 1:
        return no_time[0][1], no_time[0][2]
    return '', ''


def read_sirena(path):
    df = pd.read_fwf(path, colspecs=list(SIRENA_COLUMNS.values()), names=list(SIRENA_COLUMNS),
                     skiprows=1, dtype=str, keep_default_na=False)
    df['doc'] = df['doc'].str.replace(' ', '')
    df['dep_date'] = df['dep_date'].map(dmy)
    tickets, names = {}, {}
    for r in df.itertuples(index=False):
        key = (r.doc, r.flight_no, r.dep_date)
        tickets[key] = {'ticket': r.ticket_no, 'from': r.dep_airport, 'to': r.arr_airport}
        names[key] = tuple(translit(w) for w in r.name.split())
    return tickets, names


def read_boarding(path):
    df = pd.read_csv(path, sep=';', dtype=str, keep_default_na=False)
    df['key'] = list(zip(df['PassengerDocument'].str.replace(' ', ''), df['FlightNumber'], df['FlightDate'].map(dmy)))
    df['TicketNumber'] = df['TicketNumber'].replace('Not presented', '')
    return df.to_dict('records')


def main(boarding_path, sirena_path, flights_path, dst):
    tickets, sirena_names = read_sirena(sirena_path)
    from_sirena = len(tickets)

    foreign_by_ticket = {}
    foreign_by_name = defaultdict(list)
    for key, t in tickets.items():
        if len(key[0]) == 9:
            foreign_by_ticket[t['ticket']] = key
            last, first, middle = sirena_names[key]
            foreign_by_name[(key[1], key[2], last, first)].append((key, middle))

    boarding = read_boarding(boarding_path)

    city_airports = defaultdict(Counter)
    for r in boarding:
        if t := tickets.get(r['key']):
            city_airports[r['Destination']][t['to']] += 1
    city_airport = {city: c.most_common(1)[0][0] for city, c in city_airports.items() if len(c) == 1}

    flights = load_flights(flights_path)
    merged_by_ticket = merged_by_name = 0
    for r in boarding:
        key = r['key']
        ticket = r['TicketNumber']
        if key in tickets:
            tickets[key]['ticket'] = tickets[key]['ticket'] or ticket
            continue

        same = foreign_by_ticket.get(ticket) if ticket else None
        if same in tickets and same[1:] == key[1:]:
            merged_by_ticket += 1
        else:
            middle = r['PassengerSecondName'].strip().rstrip('.')
            found = [k for k, m in foreign_by_name.get((key[1], key[2], r['PassengerLastName'], r['PassengerFirstName']), [])
                     if k in tickets and m.startswith(middle)]
            same = found[0] if len(found) == 1 else None
            merged_by_name += same is not None
        if same:
            tickets[key] = tickets.pop(same)
            tickets[key]['ticket'] = tickets[key]['ticket'] or ticket
            continue

        frm, to = find_route(flights.get(key[1:], []), r['FlightTime'], city_airport.get(r['Destination']))
        tickets[key] = {'ticket': ticket, 'from': frm, 'to': to}

    with open(dst, 'w', encoding='utf-8', newline='') as f:
        w = csv.writer(f)
        w.writerow(OUT_FIELDS)
        for (passport, flight_no, date), t in tickets.items():
            w.writerow([passport, flight_no, date, t['ticket'], t['from'], t['to']])

    print(f'Sirena: билетов {from_sirena}; BoardingData.csv: строк {len(boarding)}')
    print(f'итого билетов: {len(tickets)}, без номера: {sum(1 for t in tickets.values() if not t["ticket"])}')


if __name__ == '__main__':
    if len(sys.argv) != 5:
        sys.exit(__doc__)
    main(*sys.argv[1:])
