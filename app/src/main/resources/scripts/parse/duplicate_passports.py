import csv
import sys
from collections import defaultdict


def main(src, dst):
    by_passport = defaultdict(list)
    with open(src, encoding='utf-8', newline='') as f:
        reader = csv.DictReader(f)
        fields = reader.fieldnames
        for r in reader:
            by_passport[r['passport']].append(r)

    duplicates = {p: people for p, people in by_passport.items() if len(people) > 1}

    with open(dst, 'w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for people in duplicates.values():
            w.writerows(people)

    print(f'паспортов: {len(by_passport)}, из них на нескольких людях: {len(duplicates)}')
    for passport, people in duplicates.items():
        names = '; '.join(f"{p['last_name']} {p['first_name']} {p['middle_name']} {p['birth_date']}" for p in people)
        print(f'  {passport}: {names}')


if __name__ == '__main__':
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])
