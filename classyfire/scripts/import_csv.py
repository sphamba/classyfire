import csv
from classyfire.database import entries_table, columns_table


def import_csv(csv_path):
    entries_table.truncate()

    with open(csv_path, "r") as file:
        reader = csv.reader(file, delimiter=",", quotechar='"')
        next(reader)  # skip header
        for row in reader:
            entry = {}
            for i, col in enumerate(columns_table.all()):
                if col["type"] == "tags":
                    tags = row[i].split(",")
                    tags = [tag.strip() for tag in tags if tag.strip()]
                    if col["key"] != "authors":
                        tags = [tag.lower() for tag in tags]
                    entry[col["key"]] = tags

                else:
                    entry[col["key"]] = row[i].strip()

            print(entry)
            entries_table.insert(entry)


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Usage: python import_csv.py <path-to-csv-file>")
    csv_path = sys.argv[1]

    import_csv(csv_path)
