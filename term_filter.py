import csv
import time
import deep_translator
translator = deep_translator.GoogleTranslator(source='auto', target='en')
# -*- coding: utf-8 -*-
# process: <sourcelink, vid, TC, title, description, tags>
# get: raw_classified file and npy file <vid, lables>

#TODO 5.7w filtered to 5.4w, the rules are too loose

categories = []
with open('./tables/10cates.txt', 'r', encoding='utf-8') as file: #refined by professional
    reader = csv.reader(file)
    for row in reader: #转小写、去引号
        temp = [x.lower().replace('\"', '').strip() for x in row[0].split('OR')]
        categories.append(temp)


def detect_translate(row):
    new_row = row[:2]
    for s in row[2:]:
        try:
            s.encode(encoding='utf-8').decode('ascii')
            new_row.append(s)
        except UnicodeDecodeError:
            try:
                trans = translator.translate(s)
                if trans: new_row.append(trans)
                else: new_row.append("") # special characters like •
            except deep_translator.exceptions.RequestError:
                time.sleep(2) # google api allows 5 requests per second max
                # new_row.append(translator.translate(s))
                print(row[1]) # TODO don't know why
                new_row.append("")
    return new_row


def hit(infot):
    hit = set()
    hit_cates = ""
    for i, cate_labels in enumerate(categories):
        for c in cate_labels:
            if c in infot:
                if ' ' in c or c == 'phaco':#multi-word term 'phaco' is just too much
                    hit.add(i)
                    hit_cates += c + ';'
                else:
                    if c in infot.split(' ') or c+',' in infot or c+'.' in infot or c+';' in infot or c+'-' in infot or '-'+c in infot:
                        hit.add(i)
                        hit_cates += c + ';'
    return list(hit), hit_cates


def easy_resume(filePointer, last_vid='6QeW-huMDQA'):
    for row in csv.reader(filePointer):
        if last_vid in row[1]: break
    
    
with open('./tables/vidInfo3.csv', 'r', newline='', encoding='utf-8') as file,\
     open("./tables/vidInfo3_rawClassfied2.csv", 'w', newline='', encoding='utf-8') as filed:
    easy_resume(file)
    reader = csv.reader(file)
    writer = csv.writer(filed)
    for row in reader:
        row = detect_translate(row)
        # rule1: filter by TC
        if row[2] not in ['healthknowledge', 'health', 'healthsociety', 'knowledge',
                      'healthsocietytelevision_program', '', 'healthknowledgetelevision_program',
                      'technology', 'healthlifestyle_(sociology)', 'knowledgetechnology', 'healthtechnology',
                      'societytelevision_program', 'lifestyle_(sociology)']: continue
        # rule2: title should not contain
        if any(x in row[3] for x in ['examination', 'sign', 'symptoms', 'Tomography', 'observ', 'animation']): continue
        
        text = ' '.join(row[3:])
        h,hc = hit(text.lower())
        #rule3: discard rows with empty TC, and no hit, and contain non of these keywords
        if row[2] == '' and len(h) == 0 and \
            not any(x in row[5:] for x in ['surgery', 'operation', 'technique', 'technology', 'management']) and \
            not any(x in row[3] for x in ['surgery', 'operation', 'technique', 'technology', 'management']): continue

        row.insert(3, hc)
        row.insert(4, ','.join([str(i) for i in h]))
        writer.writerow(row)


# count = [0] * 11
# for r in ret:
#     count[r] += 1
# cates = [c[0] for c in categories]
# print(cates)
# print(count)