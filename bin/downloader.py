from argparse import ArgumentParser
import json
import os
import csv
import optparse
import playlist_items
import channel_info
import video_info
from multiprocessing import Pool

#HAVEDONE:
# - 实现Youtube视频元数据解析，vid, title, description, tags存表

cmd = "yt-dlp -f best -f mp4 \'https://www.youtube.com/watch?v=%s\' -o ../../YtbEyeVideos/%s.mp4"
def process(vid):
    os.system(cmd % (vid, vid)) 

def crosscheck_videos(video_path, vids): # Get non-existing videos
    existing_vids = [video[:11] for video in os.listdir(video_path)]
    return [vid[:11] for vid in vids if vid[:11] not in existing_vids]


def getVids():
    # Parse meta info an return video IDs
    vids = []

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
    options, _ = parser.parse_args()
    
    with open('../lowQualityPlaylist.csv', 'r', encoding='utf-8')as file:
        reader = csv.reader(file) #['Src', 'Link', 'Total', '#Surgery']
        for row in reader:
            if "playlist" in row[1]:
                options.url = row[1]
                collections = playlist_items.main(options)
            else:
                options.url = False # ban this param which is repeated with playlist module
                options.cUrl = row[1]
                cinfo = channel_info.main(options)
                options.plid = cinfo['contentDetails']["relatedPlaylists"]["uploads"]
                collections = playlist_items.main(options)
                print(collections['totalVideos'])
                options.plid = False # reset this param
            vids.extend(collections['videoIDs'])
    
    print("# vids:", len(vids))
    with open('../vids2.txt', 'w', encoding='utf-8') as f:
        for vid in vids:
            f.write(vid+'\n')

def getInfo():
    with open('../vids2.txt', 'r', encoding='utf-8') as f:
        vids = f.readlines()
    # vids = vids[12676:]

    # parse video metadate vid by vid
    parser2 = optparse.OptionParser()
    parser2.add_option("-u", "--url", dest = "url" , default=False, help="video url as input")
    parser2.add_option("-i", "--id", dest = "id", default=False, help="video id as input")
    parser2.add_option('-p',"--popular", dest = "popular", action="store_true", default=False, help="most popular videos")
    parser2.add_option("--region", dest = "regionCode", default=False, help="popular videos per region")
    parser2.add_option('-r',"--results", dest = "maxResults", default=False, help="search max result number")
    parser2.add_option('-d',"--display", dest = "display", action="store_true", default=False, help="display query response")
    parser2.add_option('-b',"--basic", dest = "basic", action="store_true", default=True, help="display query basic info")
    (options,args) = parser2.parse_args()

    with open('../vidInfo2.csv', 'a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file) #[vid, title, description, tags], tags is non-fix length
        for vid in vids:
            options.id = vid[:-1] #remove '\n'
            collections = video_info.main(options)
            if len(collections) == 0: continue
            print(vid)
            ret = [vid[:-1], collections['title'], collections['description']]
            ret.extend(collections['tags'])
            writer.writerow(ret)


def main():
    # getVids()
    # getInfo()
    with open('../tables/vids7w.txt', 'r', encoding='utf-8') as f:
        vids = f.readlines()
    vids = crosscheck_videos("../../YtbEyeVideos", vids)
    
    with Pool(processes=os.cpu_count()) as pool:
        pool.map(process, vids)

if __name__ == "__main__":
    main()