import csv
# -*- coding: utf-8 -*-

# 1.眼睑手术"eyelid"
# 2.泪器手术"lacrimal"
# 3.结膜手术"Conjunctival Surgery
# 4.巩膜手术"Scleral Surgery"
# 5.晶状体手术"Cataract"
# 6.前房手术"iris surgery"
# 7.青光眼手术"glaucoma"
# 8.玻璃体视网膜脉络膜手术"macular hole"
# 9.眼眶手术"Orbital surgery"
# 10.眼外肌手术"ocular muscle surgery"
categories = []
with open('./tables/10cates.txt', 'r', encoding='utf-8') as file: #refined by professional
    reader = csv.reader(file)
    for row in reader: #转小写、去引号
        temp = [x.lower().replace('\"', '').strip() for x in row[0].split('OR')]
        # for x in temp:
        #     if ' ' not in x: print(x)
        categories.append(temp)

#hitted labels vote for category
def hit(infot):
    hit = 10 #invalid cate number represents no hit
    most_vote = 0
    hit_cates = ""
    for i, cate_labels in enumerate(categories):
        vote = 0
        for c in cate_labels:
            if c in infot:
                if ' ' in c or c == 'phaco':#multi-word term 'phaco' is just too much
                    vote += 1
                    hit_cates += c + ';'
                else: # single word should not contained in another word
                    #eg: 'retinal' could be contained in a word "Vitreoretinal Fellow of  Sankara Nethralaya, Chennai"
                    if c in infot.split(' ') or c+',' in infot or c+'.' in infot or c+';' in infot or c+'-' in infot or '-'+c in infot:
                        vote += 1
                        hit_cates += c + ';'
        if vote > most_vote:
            most_vote = vote
            hit = i
    return hit, hit_cates


ret = []
vidInfoWithCate = []
with open('./tables/test.csv', 'r', newline='', encoding='utf-8') as file:
    reader = csv.reader(file)
    # count = 30
    for row in reader:
        text = ' '.join(row[1:])
        h,hc = hit(text.lower())
        ret.append(h)
        row.insert(1, hc)
        vidInfoWithCate.append(row)
        
        # count -= 1
        # if count == 0: break

with open('./tables/test_rawClassfied2.csv', 'w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerows(vidInfoWithCate)

count = [0] * 11
for r in ret:
    count[r] += 1
cates = [c[0] for c in categories]
print(cates)
print(count)


# log:
# [259, 20, 773, 263, 8184, 81, 1006, 1440, 24, 27, 8809]
# [258, 20, 742, 219, 9177, 58, 1467, 1341, 24, 26, 7554] add two terms "glaucoma" and "Cataract" and "Cataracts"
# [258, 20, 742, 219, 9185, 58, 1467, 1341, 24, 26, 7546] or c+'-' in split
# [259, 20, 723, 177, 11489, 40, 1156, 1189, 24, 26, 5783] "phaco" add "Phaco chop techniques" and "direct chop" and "Prechopper" and "prechop" and "CHOPPER" and "IOL"
# [261, 20, 745, 174, 11694, 37, 1217, 1231, 24, 26, 5457] c+','
# [260, 20, 751, 175, 12405, 36, 1189, 1280, 21, 21, 4728] 'phaco' special treatment
# [260, 20, 748, 150, 12725, 34, 1158, 1211, 20, 21, 4539] 'lens', 'SICS'
# [260, 20, 748, 142, 12766, 34, 1232, 1187, 20, 21, 4456] c+';'
# [259, 29, 748, 142, 12766, 34, 1232, 1187, 21, 21, 4447] add by zefeng