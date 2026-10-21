import sys

import pandas as pd


def main(src, dst):
    people = pd.read_csv(src, dtype=str, keep_default_na=False)
    duplicates = people[people.duplicated('passport', keep=False)]
    groups = duplicates.groupby('passport', sort=False)

    pd.concat([group for _, group in groups] or [duplicates]).to_csv(dst, index=False, lineterminator='\r\n')

    print(f"паспортов: {people['passport'].nunique()}, из них на нескольких людях: {groups.ngroups}")
    for passport, group in groups:
        names = '; '.join(f'{p.last_name} {p.first_name} {p.middle_name} {p.birth_date}' for p in group.itertuples())
        print(f'  {passport}: {names}')


if __name__ == '__main__':
    if len(sys.argv) != 3:
        sys.exit('Запуск: python duplicate_passports.py passengers.csv duplicate_passports.csv')
    main(sys.argv[1], sys.argv[2])
