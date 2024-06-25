import csv
import optparse
import playlist_items
import channel_info
import video_info
import shutil

'''
Youtube视频元数据解析，<sourcelink, vid, (TC,) title, description, tags>存表
TC(topic categories)为新启用信息，不一定每个视频都有，用于辅助后续术语分类与过滤。

TODO:
- 会莫名卡住，无报错
- 有否2K，4K
- deprecated warning, arguments of new tool
- parse playlist name
'''


def resume(source_reader, source, filed):
    shutil.copyfile("./tables/vidInfo3.csv", "./vidInfo3_backup.csv")

    broke_row = None
    for broke_row in csv.reader(filed): pass

    #移动source_reader指针到上次断开的位置，引用传值进函数并修改之，作用域是全局的。
    #但如果直接移动它, break后就已经指向了下一行，所以让它作为一个慢指针去移动
    #并且实际上移动的是files，source_reader只是包括了files和一些IO方法的对象，既不能直接深拷贝（TextIOWrapper无法被序列化），
    #也不能通过新构造一个csvreader获得一个新指针，新的对象包含的还是老指针
    #files本身也不能解引用，只能从最源头获取一个新指针，还好csv好对付。
    fast_pointer = open(source, 'r', encoding='utf-8')
    for row in fast_pointer:
        current_link = row.split(',')[1]
        if current_link == broke_row[0]: break #前提是保证链接表不重复
        next(source_reader)
    fast_pointer.close()
    return broke_row[1][1:-1] # return last vid

def remove_null_in_list(row_list): # the binary nulls interrupt csv reader enumerating
    return [''.join([c for c in s if ord(c) != 0]) for s in row_list]

def getOptionParsers():
    parser = optparse.OptionParser()
    # args of playlist parsing module
    parser.add_option("-u", "--url", dest = "url" , default=False, help="playlist URL")
    parser.add_option("-i", "--id", dest = "plid", default=False, help="playlist ID")
    parser.add_option('-d',"--display", dest = "display", action="store_true", default=False, help="display query response")
    # args of channel parsing module
    parser.add_option("--chid", dest = "chid", default=False, help="channel ID")
    parser.add_option("-n", "--username", dest = "user" , default=False, help="channel username")
    parser.add_option("-c", "--cUrl", dest = "cUrl" , default=False, help="custom channel url")
    parser.add_option('-b',"--basic", dest = "basic", action="store_true", default=False, help="display query basic info")

    parser2 = optparse.OptionParser()
    #args of video parsing module
    parser2.add_option("-u", "--url", dest = "url" , default=False, help="video url as input")
    parser2.add_option("-i", "--id", dest = "id", default=False, help="video id as input")
    parser2.add_option('-p',"--popular", dest = "popular", action="store_true", default=False, help="most popular videos")
    parser2.add_option("--region", dest = "regionCode", default=False, help="popular videos per region")
    parser2.add_option('-r',"--results", dest = "maxResults", default=False, help="search max result number")
    parser2.add_option('-d',"--display", dest = "display", action="store_true", default=False, help="display query response")
    parser2.add_option('-b',"--basic", dest = "basic", action="store_true", default=True, help="display query basic info")
    
    return parser.parse_args()[0], parser2.parse_args()[0]

def main(source, destination, resume_flag=True):
    options, options2 = getOptionParsers()
    
    with open(source, 'r', encoding='utf-8')as files, \
        open(destination, 'r+', newline='', encoding='utf-8') as filed:
        reader = csv.reader(files) #['Src', 'Link', 'Total', '#Surgery']
        writer = csv.writer(filed) #refer to the top comments
        if resume_flag: last_vid = resume(reader, source, filed)

        for row in reader:
            if "playlist" in row[1]:
                options.url = row[1]
                collections = playlist_items.main(options)
            else:
                options.url = False # ban this param which conflicts with playlist module
                options.cUrl = row[1]
                cinfo = channel_info.main(options)
                options.plid = cinfo['contentDetails']["relatedPlaylists"]["uploads"]
                collections = playlist_items.main(options)
                options.plid = False # reset this param

            vids = collections['videoIDs']
            if resume_flag:
                pos = vids.index(last_vid)
                resume_flag = False
                print("resume from ", pos, " / ", len(vids))
                vids = vids[pos:] # the last row might be broken, so download it again
            print(row[0], collections['totalVideos'])

            # parse video metadata vid by vid
            for vid in vids:
                options2.id = vid
                collections2 = video_info.main(options2)
                if len(collections2) == 0: continue #可能是失效或付费视频
                ret = [row[1],
                        '\''+vid+'\'',
                        ''.join(collections2["topicCategories"]),
                        collections2['title'], collections2['description']]
                ret.extend(collections2['tags'])
                writer.writerow(remove_null_in_list(ret))


if __name__ == "__main__":
    main("./tables/lowQualitySrcChannel.csv", "./tables/vidInfo3.csv")