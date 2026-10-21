import json
import csv
import sys

USAGE = 'Запуск: python unknown_frequent_flyers.py <forum_profiles.json> <output.csv> [min_flights_threshold]'


def find_anonymous_frequent_flyers(json_path, min_flights):
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    suspicious_users = []

    for profile in data.get("Forum Profiles", []):
        real_name = profile.get("Real Name", {})
        first_name = real_name.get("First Name")
        last_name = real_name.get("Last Name")

        is_anonymous = not first_name and not last_name

        flights = profile.get("Registered Flights", [])
        flight_count = len(flights)

        if is_anonymous and flight_count > min_flights:
            nickname = profile.get("NickName", "Unknown")
            suspicious_users.append({
                "Никнейм": nickname,
                "Имя": first_name if first_name else "",
                "Фамилия": last_name if last_name else "",
                "Количество_перелетов": flight_count
            })

    return suspicious_users


def main(json_path, csv_path, min_flights=28):
    min_flights = int(min_flights)

    try:
        results = find_anonymous_frequent_flyers(json_path, min_flights)

        if results:
            with open(csv_path, 'w', encoding='utf-8-sig', newline='') as csvfile:
                fieldnames = ["Никнейм", "Имя", "Фамилия", "Количество_перелетов"]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=';')

                writer.writeheader()
                writer.writerows(results)

            print(f"Готово! Найдено подозрительных профилей: {len(results)}. Результаты сохранены в файл '{csv_path}'.")
        else:
            print("Анонимных часто летающих пассажиров не найдено.")

    except FileNotFoundError:
        sys.exit(f"Файл {json_path} не найден.")
    except Exception as e:
        sys.exit(f"Произошла ошибка: {e}")


if __name__ == "__main__":
    if len(sys.argv) not in (3, 4):
        sys.exit(USAGE)

    main(*sys.argv[1:3], *sys.argv[3:])