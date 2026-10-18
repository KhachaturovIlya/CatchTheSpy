import csv
import sys
from collections import defaultdict
from datetime import datetime

OUT_FIELDS = ['passport', 'flight_no', 'dep_date', 'ticket_no', 'from_airport', 'to_airport']


def load_flights(path):
    """(flight_no, dep_date) -> список (dep_time, from, to)."""
    flights = defaultdict(list)
    with open(path, encoding='utf-8', newline='') as f:
        for r in csv.DictReader(f):
            flights[(r['flight_no'], r['dep_date'])].append((r['dep_time'], r['from_airport'], r['to_airport']))
    return flights


def find_route(candidates, time):
    """-> (from, to) или ('', '')."""
    candidates = [c for c in candidates if c[0] == time]
    if len(candidates) == 1:
        return candidates[0][1], candidates[0][2]
    return '', ''


def main(src, flights_path, dst):
    flights = load_flights(flights_path)
    rows = found = 0
    with open(src, encoding='utf-8', newline='') as fin, open(dst, 'w', encoding='utf-8', newline='') as fout:
        w = csv.writer(fout)
        w.writerow(OUT_FIELDS)
        for r in csv.DictReader(fin, delimiter=';'):
            date = datetime.strptime(r['FlightDate'], '%Y-%m-%d').strftime('%d.%m.%Y')
            frm, to = find_route(flights.get((r['FlightNumber'], date), []), r['FlightTime'])
            ticket = r['TicketNumber'] if r['TicketNumber'] != 'Not presented' else ''
            w.writerow([r['PassengerDocument'].replace(' ', ''), r['FlightNumber'], date, ticket, frm, to])
            rows += 1
            found += bool(frm)

    print(f'билетов: {rows}, с откуда/куда: {found}, без: {rows - found}')


if __name__ == '__main__':
    if len(sys.argv) != 4:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2], sys.argv[3])
