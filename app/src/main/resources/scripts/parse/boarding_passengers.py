# Запуск: python3 boarding_passengers.py {путь до входного .csv файла} {путь до итогового файла}

import csv
import sys
from datetime import datetime

SEX = {'Male': 'M', 'Female': 'F'}
OUT_FIELDS = ['passport', 'last_name', 'first_name', 'middle_name', 'birth_date', 'sex']


def main(src, dst):
    people = {}  # (passport, last, first, birth, sex) -> middle
    rows = 0
    with open(src, encoding='utf-8', newline='') as f:
        for r in csv.DictReader(f, delimiter=';'):
            key = (
                r['PassengerDocument'].replace(' ', ''),
                r['PassengerLastName'].strip(),
                r['PassengerFirstName'].strip(),
                datetime.strptime(r['PassengerBirthDate'], '%m/%d/%Y').strftime('%d.%m.%Y'),
                SEX[r['PassengerSex']],
            )
            middle = r['PassengerSecondName'].strip().rstrip('.')
            # полное отчество важнее инициала
            if len(middle) > len(people.get(key, '')):
                people[key] = middle
            rows += 1

    with open(dst, 'w', encoding='utf-8', newline='') as f:
        w = csv.writer(f)
        w.writerow(OUT_FIELDS)
        for (passport, last, first, birth, sex), middle in people.items():
            w.writerow([passport, last, first, middle, birth, sex])

    print(f'строк: {rows}, пассажиров: {len(people)}')


if __name__ == '__main__':
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])
