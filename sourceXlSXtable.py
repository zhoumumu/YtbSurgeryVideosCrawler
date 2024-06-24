import xlrd
import csv
import re
import chardet

#筛选高质量视频源（无效视频<5 OR 总视频数<20），这部分的无效视频可以手筛，剩下的要下载前过滤
#其中包含了1个非Youtube源， 124个Youtube源信息存csv了
#筛选7个低质量playlists视频源（lowQualitySrcPlaylist.csv）


wb = xlrd.open_workbook('./tables/videoSrc_list_RMduplicated.xlsx')
#按工作簿定位工作表
sh = wb.sheet_by_name('YouTube视频等收集')
# print(sh.nrows)#有效数据行数
# print(sh.ncols)#有效数据列数
# print(sh.cell(0,0).value)#输出第一行第一列的值
# print(sh.row_values(0))#输出第一行的所有值

def remove_non_gbk_chars(string):
    pattern = re.compile(r'[\xae\ufe0f\u011f\u015f\u0131\u0159\xcd]') #®、非英语人名...没完没了
    cleaned = pattern.sub('', string)
    return cleaned

highQualitySrc = []
highQualitySrcU = []
lowQualitySrcPlaylist = []
lowQualitySrcChannel = []
ytb_total = 0
for i in range(1, sh.nrows-1):
    # if 'youtube' in sh.cell(i,1).value:
    #     ytb_total += 1

    # src = remove_non_gbk_chars(sh.cell(i,0).value)

    if int(sh.cell(i,2).value) < 20 or\
      int(sh.cell(i,2).value) - int(sh.cell(i,3).value) < 5:
        if 'youtube' in sh.cell(i,1).value:
            highQualitySrcU.append([sh.cell(i,0).value, sh.cell(i,1).value,
                               sh.cell(i,2).value, sh.cell(i,3).value])
        else:
            highQualitySrc.append([sh.cell(i,0).value, sh.cell(i,1).value,
                               sh.cell(i,2).value, sh.cell(i,3).value])
    else:
        if 'playlist' in sh.cell(i,1).value:
            lowQualitySrcPlaylist.append([sh.cell(i,0).value, sh.cell(i,1).value,
                               sh.cell(i,2).value, sh.cell(i,3).value])
        else:
            lowQualitySrcChannel.append([sh.cell(i,0).value, sh.cell(i,1).value,
                               sh.cell(i,2).value, sh.cell(i,3).value])

# print(ytb_total)
# print(len(highQualitySrc), len(highQualitySrcU))
# print(highQualitySrcU)

# with open('highQualitySrcU.csv', 'w', newline='', encoding='utf-8') as file2:
#     writer = csv.writer(file2) #['Src', 'Link', 'Total', '#Surgery']
#     writer.writerows(highQualitySrcU)

# with open('../lowQualitySrcPlaylist.csv', 'w', newline='', encoding='utf-8') as file2:
#     writer = csv.writer(file2) #['Src', 'Link', 'Total', '#Surgery']
#     writer.writerows(lowQualitySrcPlaylist)

with open('./tables/lowQualitySrcChannel.csv', 'w', newline='', encoding='utf-8') as file2:
    writer = csv.writer(file2) #['Src', 'Link', 'Total', '#Surgery']
    writer.writerows(lowQualitySrcChannel)
    