import csv

###################################
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


###################################
# process nohit, make analysis
# multihit = []
# with open('./tables/vidInfo_rawClassfied2.csv', 'r', newline='', encoding='utf-8') as file,\
#     open('../nohit2.csv', 'w', newline='', encoding='utf-8') as f:
#     reader = csv.reader(file)
#     for row in reader:
#         if len(row[1].strip().split(';')) == 1:
#             multihit.append(row)

#     print(len(multihit))
#     writer = csv.writer(f)
#     writer.writerows(multihit)


###################################
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


###################################
# _csv.Error: line contains NUL, which is b'\x00'
# NULL keep csv reader from enumerating, we can remove them in binary mode
# analyze topic catagory
# f = open('./tables/vidInfo3.csv', 'rb')
# data = f.read()
# # print(data.find(b'\x00'))
# # print(data.find(0))
# # print(data[110721])
# # for i, c in enumerate(data):
# #     if c == 0:
# #         print(repr(data[i-30:i]) + ' *NUL* ' + repr(data[i+1:i+31]))
# f = open('./tables/vidInfo3.csv', 'r', encoding='utf-8')
# for c in f.read():
#     if ord(c) == 0:
#         print("sdga")
# f.close()
# data = data.replace(b'\x00', b'')
# # print(data.count(b'\x00'))
# new_f = open('./tables/samples.csv', 'wb')
# new_f.write(data)
# new_f.close()

# TC = {}
# with open('./tables/samples.csv', 'r', newline='', encoding='utf-8') as file:
#     reader = csv.reader(file)
#     for row in reader:
#         if row[2] not in TC:
#             TC[row[2]] = 1
#         else:
#             TC[row[2]] += 1
# print(len(TC)) #54
# print(sorted(TC.items(), key=lambda x:x[1], reverse=True))
#头部TC：healthknowledge', 5330), ('health', 208), ('healthsociety', 168), ('knowledge', 63), ('healthsocietytelevision_program', 48), ('', 33)
#除去如Music这样的显著不合理的，还打算保留的TC：('healthknowledgetelevision_program', 28), ('technology', 25), ('healthlifestyle_(sociology)', 21)，('knowledgetechnology', 9), ('healthtechnology', 8)， ('societytelevision_program', 4)
#抽查不合格TC：('society', 33), ('hobbylifestyle_(sociology)', 3), 合格TC：'lifestyle_(sociology)', 16)
# #make grouping rules
# for tc in TC:
#     if 'health' in tc: continue
#     print(tc)


# ###################################
# # vidInfo3.csv is broken bcuz of wps
# with open('./tables/vidInfo3.csv', 'r', newline='', encoding='utf-8') as file,\
#      open('G:vidInfo3_backup1.csv', 'r', newline='', encoding='utf-8') as file2,\
#      open('./vidInfo3_backup1.csv', 'w', newline='', encoding='utf-8') as file3:
#     vids = set()
#     unbroken = []

#     reader = csv.reader(file2)
#     for row in reader:
#         if row[1] not in vids:
#             vids.add(row[1])
#             unbroken.append(row)

#     reader = csv.reader(file)
#     for row in reader:
#         if row[1] not in vids:
#             vids.add(row[1])
#             unbroken.append(row)

#     writer = csv.writer(file3)
#     writer.writerows(unbroken)

with open('./tables/vidInfo3.csv', 'r', newline='', encoding='utf-8') as file,\
     open('./vidInfo3.csv', 'w', newline='', encoding='utf-8') as file2:
    reader = csv.reader(file)
    writer = csv.writer(file2)
    for row in reader:
        # these broken lines cause google translate api encounter connection error
        # they are non surgery videos, just remove them
        if 'r3kw-EUfp_w' in row[1] or 'aQP32wekSYo' in row[1] or '0wJSJsXU5Zw' in row[1] or '7nleNIyJK-8' in row[1]:
            print("found")
            continue
        if len(row) < 3:
            print(row)
            continue
        writer.writerow(row)

