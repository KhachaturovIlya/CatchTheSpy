import sys
from math import comb

import pandas as pd

USAGE = 'Запуск: python delayed_baggage.py BoardingData.csv delayed_baggage.csv [min_delayed]'


def expected_people(flights_per_person, p, k):
    return sum(sum(comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(k, n + 1)) for n in flights_per_person)


def main(src, dst, min_delayed=3):
    df = pd.read_csv(src, sep=';', dtype=str, keep_default_na=False)
    df['passport'] = df['PassengerDocument'].str.replace(' ', '')
    df['delayed'] = df['Baggage'] == 'Delayed'
    df['flight'] = (df['FlightNumber'] + ' ' + pd.to_datetime(df['FlightDate']).dt.strftime('%d.%m.%Y')
                    + ' ' + df['Destination'])

    key = ['passport', 'PassengerLastName', 'PassengerFirstName']
    df['middle'] = df['PassengerSecondName'].str.rstrip('.')
    df['middle_len'] = df['middle'].str.len()
    people = df.groupby(key, sort=False).agg(flights=('delayed', 'size'), delayed=('delayed', 'sum'))
    people['middle_name'] = df.sort_values('middle_len').groupby(key)['middle'].last()
    people['delayed_flights'] = df[df['delayed']].groupby(key)['flight'].agg('; '.join)
    people = people.reset_index().fillna({'delayed_flights': ''})
    people = people.rename(columns={'PassengerLastName': 'last_name', 'PassengerFirstName': 'first_name'})
    people['delayed_share'] = (people['delayed'] / people['flights']).round(2)

    result = people[people['delayed'] >= min_delayed].sort_values(['delayed', 'delayed_share'], ascending=False)
    result[['passport', 'last_name', 'first_name', 'middle_name', 'flights', 'delayed', 'delayed_share',
            'delayed_flights']].to_csv(dst, index=False, lineterminator='\r\n')

    p = df['delayed'].mean()
    print(f'рейсов: {len(df)}, багаж задержан: {df["delayed"].sum()} ({p:.0%})')
    for r in result.head(10).itertuples():
        print(f'  {r.passport} {r.last_name} {r.first_name}: {r.delayed} из {r.flights}')


if __name__ == '__main__':
    if len(sys.argv) not in (3, 4):
        sys.exit(USAGE)
    main(*sys.argv[1:3], *(int(x) for x in sys.argv[3:]))
