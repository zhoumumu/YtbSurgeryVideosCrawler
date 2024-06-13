import csv

#转小写、去引号、去surgery
categories = []
# with open('../terms.txt', 'r', encoding='utf-8') as file:
# with open('../terms_del.txt', 'r', encoding='utf-8') as file: #removed 4 repeated terms
# with open('../categories.txt', 'r', encoding='utf-8') as file: #labels rather than search terms, only 92 videos hit
with open('../10cates.txt', 'r', encoding='utf-8') as file: #refined by professional
    reader = csv.reader(file)
    for row in reader:
        # temp = [x.lower().replace('surgery', '').replace('\"', '').strip() for x in row[0].split('OR')]
        temp = [x.lower().replace('\"', '').strip() for x in row[0].split('OR')]
        categories.append(temp)
# print(categories[4]) #lens这一类视频异常多，但打出来看看处理得也没啥问题

#看处理后的检索词是否有重叠，一条视频会否命中多个类别
# set_categories = [set(c) for c in categories]
# for i in range(15):
#     for j in range(i+1, 15):
#         if set_categories[i] & set_categories[j]:
#             print(i, j)
#             print(set_categories[i] & set_categories[j])
# 6 14
# {'laser iridotomy'}
# 7 14
# {'selective laser trabeculoplasty'}
# 9 10
# {'endolaser photocoagulation'}
# 9 14
# {'laser retinopexy'}
# 10 11
# {'intraocular tumor biopsy', 'extraction of intra-ocular foreign body', 'intraocular tumor cryotherapy', 'enucleation of eyeball', 'choroidectomy', 'plaque brachytherapy', 'ocular tumor surgeries', 'eye cancer'}


def hit(cate_labels, infot):
    #return True if any label is in infot
    for c in cate_labels:
        if c in infot and ' '+c+' ' in infot: #eg: 'retinal' could be contained in a word
            return (True, c)
    return (False, '')


ret = []
# videos with tags, only 7560 / 20886
vidInfoWithCate = []
with open('../vidInfo.csv', 'r', newline='', encoding='utf-8') as file:
    reader = csv.reader(file)
    for row in reader:
        text = ' '.join(row[1:])
        nohit = True
        hit_cates = ""
        for i in range(10):
            r,c = hit(categories[i], text)
            if r:
                ret.append(i)
                nohit = False
                hit_cates += c + ';'
        if nohit: ret.append(10)
        row.insert(1, hit_cates)
        vidInfoWithCate.append(row)
with open('../vidInfo_rawClassfied.csv', 'w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerows(vidInfoWithCate)

count = [0] * 11
for r in ret:
    count[r] += 1
cates = [c[0] for c in categories]
print(cates)
print(count)
# initial pass: [286, 20, 285, 1618, 454, 12232, 128, 5863, 0, 0, 0, 0, 0, 0, 0, 0]
# removed 4 terms: [286, 20, 285, 1618, 454, 12232, 128, 5863, 0, 0, 0, 0, 0, 0, 0, 0]

