import csv

# # process multihit, make analysis
# multihit = []
# with open('../vidInfo_rawClassfied.csv', 'r', newline='', encoding='utf-8') as file,\
#     open('../multihit.csv', 'w', newline='', encoding='utf-8') as f:
#     reader = csv.reader(file)
#     for row in reader:
#         if len(row[1].strip().split(';')) > 2:
#             multihit.append(row)

#     print(len(multihit))
#     writer = csv.writer(f)
#     writer.writerows(multihit)


# process nohit, make analysis
multihit = []
with open('./tables/vidInfo_rawClassfied2.csv', 'r', newline='', encoding='utf-8') as file,\
    open('../nohit2.csv', 'w', newline='', encoding='utf-8') as f:
    reader = csv.reader(file)
    for row in reader:
        if len(row[1].strip().split(';')) == 1:
            multihit.append(row)

    print(len(multihit))
    writer = csv.writer(f)
    writer.writerows(multihit)

# get extra link in description, get more tags for potential useful terms
# tags = []
# links = []
# with open('../vidInfo.csv', 'r', newline='', encoding='utf-8') as file,\
#     open('../extraLinksInDescription.txt', 'r', encoding='utf-8') as f1:
#     reader = csv.reader(file)
#     for row in reader:
#         try:
#             pos = row[2].index("http")
#             links.append(row[2][pos:].split(' ')[0])
#         except ValueError:
#             pass
#         if len(row) > 3:
#             tags.extend(row[3:])
#     links_ = list(set(links))
#     # for t in links_:
#     #     f1.write(t+'\n')

# categories = []
# with open('../10cates.txt', 'r', encoding='utf-8') as file: #refined by professional
#     reader = csv.reader(file)
#     for row in reader:
#         temp = [x.replace('\"', '').strip() for x in row[0].split('OR')]
#         categories.extend(temp)

# with open('../extraTags.txt', 'w', encoding='utf-8') as f2:
#     tags_ = list(set(tags) - set(categories))
#     for t in tags_:
#         f2.write(t+'\n')