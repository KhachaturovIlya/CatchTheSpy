import csv
import sys

import pandas as pd

SEX = {'Male': 'M', 'Female': 'F'}
OUT_FIELDS = ['passport', 'last_name', 'first_name', 'middle_name', 'birth_date', 'sex']

SIRENA_COLUMNS = {
    'name': (0, 60),
    'birth_date': (60, 72),
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


def read_boarding(path):
    df = pd.read_csv(path, sep=';', dtype=str, keep_default_na=False)
    return pd.DataFrame({
        'passport': df['PassengerDocument'].str.replace(' ', ''),
        'last': df['PassengerLastName'].str.strip(),
        'first': df['PassengerFirstName'].str.strip(),
        'middle': df['PassengerSecondName'].str.strip().str.rstrip('.'),
        'birth': pd.to_datetime(df['PassengerBirthDate'], format='%m/%d/%Y').dt.strftime('%d.%m.%Y'),
        'sex': df['PassengerSex'].map(SEX),
    })


def read_sirena(path):
    df = pd.read_fwf(path, colspecs=list(SIRENA_COLUMNS.values()), names=list(SIRENA_COLUMNS),
                     skiprows=1, dtype=str, keep_default_na=False)
    name = df['name'].str.split(expand=True).apply(lambda col: col.map(translit))
    birth = pd.to_datetime(df['birth_date'].replace('N/A', None), format='%Y-%m-%d')
    return pd.DataFrame({
        'passport': df['doc'].str.replace(' ', ''),
        'last': name[0],
        'first': name[1],
        'middle': name[2],
        'birth': birth.dt.strftime('%d.%m.%Y').fillna(''),
    })


def main(boarding_path, sirena_path, dst):
    people = {}

    boarding = read_boarding(boarding_path)
    for r in boarding.itertuples(index=False):
        p = people.setdefault((r.passport, r.last, r.first), {'middle': r.middle, 'birth': r.birth, 'sex': r.sex})
        if len(r.middle) > len(p['middle']):
            p['middle'] = r.middle
    rows = len(boarding)
    from_boarding = len(people)
    initials_before = sum(1 for p in people.values() if len(p['middle']) == 1)

    sirena = read_sirena(sirena_path)
    for r in sirena.itertuples(index=False):
        p = people.setdefault((r.passport, r.last, r.first), {'middle': r.middle, 'birth': r.birth, 'sex': ''})
        if len(p['middle']) == 1 and r.middle.startswith(p['middle']):
            p['middle'] = r.middle
        if not p['birth']:
            p['birth'] = r.birth
    sirena_rows = len(sirena)

    with open(dst, 'w', encoding='utf-8', newline='') as f:
        w = csv.writer(f)
        w.writerow(OUT_FIELDS)
        for (passport, last, first), p in people.items():
            w.writerow([passport, last, first, p['middle'], p['birth'], p['sex']])

    added = list(people)[from_boarding:]
    initials_after = sum(1 for p in list(people.values())[:from_boarding] if len(p['middle']) == 1)
    print(f'BoardingData.csv: строк {rows}, людей {from_boarding}')
    print(f'Sirena: строк {sirena_rows}, новых людей {len(added)} ')
    print(f'итого людей: {len(people)}')


if __name__ == '__main__':
    if len(sys.argv) != 4:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2], sys.argv[3])
