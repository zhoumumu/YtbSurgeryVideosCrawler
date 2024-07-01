import os
import subprocess
import numpy as np
from multiprocessing import Pool

COUNT_FRAME = "ffprobe -v error -count_frames -select_streams v:0 -show_entries stream=nb_read_frames -of default=nokey=1:noprint_wrappers=1 {}"
SAMPLE = "ffmpeg -i {} -vf select=\'eq(n\,{})+eq(n\,{})+eq(n\,{})+eq(n\,{})+eq(n\,{})+eq(n\,{})+eq(n\,{})+eq(n\,{})\' -vsync 0 {}frames%d.jpg"

def process(vid):
    os.mkdir('./8frames_per_video/'+vid[:-4])
    _, num_frames = subprocess.getstatusoutput(COUNT_FRAME.format('train_test_data_video/'+vid))
    num_frames = num_frames.split('\n')[-1]

    pos = list(np.multiply(list(range(8)), int(num_frames)//8))
    pos = [str(x) for x in pos]

    os.system(SAMPLE.format('train_test_data_video/'+vid, pos[0], pos[1], pos[2], pos[3], pos[4], pos[5], pos[6], pos[7],
                           "8frames_per_video/"+vid[:-4]+'/'))

        
if __name__ == "__main__":
    vid_list = os.listdir('train_test_data_video')
    exist_list = os.listdir('8frames_per_video')
    for x in exist_list:
        vid_list.remove(x+'.mp4')
    
    pool = Pool(32)
    pool.map(process, vid_list)