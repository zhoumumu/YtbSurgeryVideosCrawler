import csv
import shutil


def deduplicate(file_path):
    vids = set()
    remove = 0
    rows = []
    with open(file_path, 'r', newline='', encoding='utf-8') as file:
        reader = csv.reader(file)
        for row in reader:
            if row[1] not in vids: #pay attention to this index, whether it's an id
                vids.add(row[1])
                rows.append(row)
            else:
                remove += 1
    with open(file_path, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerows(rows)
    print(f"Remove {remove} duplicated rows.")

shutil.copyfile("./tables/lowQualitySrcChannel.csv", "./lowQualitySrcChannel.csv")
deduplicate("./tables/lowQualitySrcChannel.csv")