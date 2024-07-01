import torch
import torch.nn as nn
import glob
import json
import numpy as np

from one_fc_learning import LSTM, FC
from HuaweiLoader import HuaweiLoader
from pAP import pmAP, dpAP


if __name__ == "__main__":
    net = nn.DataParallel(FC().cuda())
    checkpoint = torch.load("./save_models/mAP_CNN_6.pth")
    net.load_state_dict(checkpoint['model_state_dict'])
    optimizer = torch.optim.SGD(net.parameters(), lr=0.001, momentum=0.9)

    train_video_folder = '/opt/data/private/HuaWei/ts-features/ts-features_6/'
    train_txt = '/opt/data/private/HuaWei/data.json'
    with open(train_txt, 'r') as f:
        data = json.load(f)['videos']

    offset = [0.2]
    total = 0 #number of test video
    detection = []
    labels = []
    labels_for_print = []
    c_ts = []
    c_ts_for_print = []
    in_time = []
    in_time_for_print = []
    with torch.no_grad():
        for vid in data.keys(): #go through all the test video
            if data[vid]['subset'] != 'test':
                continue
            total += 1
            start = data[vid]['start']
            end = data[vid]['end']
            npy_paths = sorted(glob.glob(train_video_folder+vid[:-7]+'/'+vid+'/*'))

            c_tminus1 = 0
            start_flag = 0
            for npy in npy_paths: #go through all the chunks
                ip = torch.from_numpy(np.load(npy)).cuda()
                output = net(ip)
                c_t = torch.max(output.data, 1).indices

                if c_t != 0 and start_flag == 1:
                    continue

                #Got a start detection or after end
                if c_t != c_tminus1:
                    detection.append(output.squeeze().cpu().numpy().tolist())
                    c_ts.append(c_t.cpu().numpy()[0])
                    c_ts_for_print.append(c_t.cpu().numpy()[0])
                    
                    index = int(npy[-10:-4])
                    frm_last = index * 6
                    if frm_last >= start and frm_last <= end:
                        labels.append(data[vid]['label'])                  
                    else:
                        labels.append(0)
                    
                    deviation = (end-start)*0.2
                    if c_t != 0: #start
                        temp1 = abs((index-1)*6+1 - start) #chunk start - true start
                        temp2 = abs(index*6 - start) #chunk end - true start
                        if temp1 < deviation or temp2 < deviation:
                            in_time.append(True)
                            start_flag = 1
                        else:
                            in_time.append(False)
                    else: #end
                        temp1 = abs((index-1)*6+1 - end)
                        temp2 = abs(index*6 - end)
                        if temp1 < deviation or temp2 < deviation:
                            in_time.append(True)
                        else:
                            in_time.append(False)

                c_tminus1 = c_t



    #Metric 1: Rough acc
    print('Total:', total) #2879
    correct_s = correct_e = 0
    for i in range(len(in_time)):
        if c_ts[i] == labels[i] and in_time[i] and c_ts[i] != 0:
            correct_s += 1
        if c_ts[i] == labels[i] and in_time[i] and c_ts[i] == 0:
            correct_e += 1
    acc0 = correct_s / total
    acc1 = correct_e / total
    print('Acc:', acc0, acc1) #0.38 0.25

    #Metric 2: Rough separate recall
    #未过滤重复检测，假设分类准确率非常高，AS和AE匹配起来真正recall <= r_c * r_end
    count = np.zeros((46, ))
    for i in range(len(in_time)):
        if in_time[i]:
            count[c_ts[i]] += 1
    count_videos = np.zeros((46, ))
    for vid in data.keys():
        if data[vid]['subset'] != 'test':
            continue
        count_videos[data[vid]['label']] += 1
    rou_recall = count/count_videos
    rou_recall[0] = count[0] / total
    #print("test videos")
    #print(count_videos)
# [0.  60.  58. 126.  82.  73.  61.  61.  59.  68.  64.  61.  64.  62.
#  67.  60.  56.  61.  96.  21.  61.  61.  60.  59.  68.  54.  59.  61.
#  60.  58. 125.  74.  16.  63.  58.  62.  74.  75.  69.  60.  58.  61.
#  62.  20.  84.  57.]
    print("rough recall")
    print(rou_recall)
# [0.46752345, 0.05,       0.65517241, 0.,         0.42682927, 0.15068493,
#  0.62295082, 0.,         0.06779661, 0.,         0.90625,    0.18032787,
#  0.359375,   0.27419355, 0.58208955, 1.16666667, 0.46428571, 0.70491803,
#  0.42708333, 1.14285714, 0.04918033, 0.08196721, 0.76666667, 1.10169492,
#  0.11764706, 0.75925926, 0.79661017, 0.24590164, 1.,         0.0862069,
#  0.512,      0.85135135, 0.5,        1.11111111, 0.03448276, 0.03225806,
#  0.58108108, 0.,         0.,         0.28333333, 0.51724138, 1.01639344,
#  1.11290323, 0.5,        0.60714286, 0.14035088]

#when impose restriction
#end类也降了很多，说明有不少动作类被错分为背景类的情况
# [0.28273706 0.05       0.65517241 0.         0.36585366 0.1369863
#  0.59016393 0.         0.06779661 0.         0.84375    0.18032787
#  0.328125   0.27419355 0.50746269 0.65       0.44642857 0.70491803
#  0.375      0.47619048 0.04918033 0.08196721 0.76666667 0.77966102
#  0.10294118 0.7037037  0.76271186 0.21311475 0.95       0.0862069
#  0.488      0.7972973  0.5        0.92063492 0.03448276 0.03225806
#  0.55405405 0.         0.         0.26666667 0.43103448 0.91803279
#  0.9516129  0.4        0.57142857 0.14035088]


    important_cats = ['human_basketball', 'human_badminton', 'human_SplitJump', 'human_SquatJump',
                      'human_football', 'human_TableTennis', 'human_TeaseHair', 'human_rotation',
                      'object_fall', 'object_WaterBalloon', 'object_WaterDrop', 'object_CatsJump', #CATSJUMP DOES NOT EXSIT
                      'object_raining', 'object_snowflake', 'object_FallenLeaves', 'obeject_FlowersShaking',
                      'object_ FlagsShaking', 'object_ScarvesFly', 'object_ Lighter', 'object_DogsJump', #DOGSJUMP DOES NOT EXSIT
                      'object_BirdsFly', 'object_ DandelionBlowing', 'object_EggsBreak']
    important_cats = [44, 5, 26, 10,
                      29, 45, 31, 24,
                      39, 34, 38, 15, #animals_RunJump does exist
                      37, 35, 21, 9,
                      7, 20, 18,
                      19, 36, 6]
    
    recall_end = rou_recall[0]
    rough_estimation = rou_recall * rou_recall[0]
    # array([0.21857818, 0.02337617, 0.30630847, 0., 0.19955269,
    #        0.07044874, 0.29124412, 0., 0.03169651, 0.,
    #        0.42369313, 0.08430751, 0.16801624, 0.12819191, 0.27214051,
    #        0.54544403, 0.21706446, 0.32956571, 0.19967147, 0.53431251,
    #        0.02299296, 0.03832159, 0.35843465, 0.51506821, 0.05500276,
    #        0.35497151, 0.37243393, 0.11496478, 0.46752345, 0.04030375,
    #        0.23937201, 0.39802672, 0.23376173, 0.5194705, 0.0161215,
    #        0.0150814, 0.27166903, 0., 0., 0.13246498,
    #        0.24182247, 0.47518777, 0.52030836, 0.23376173, 0.28385352,
    #        0.06561733])
    good = []
    for i in range(rough_estimation.size):
        if rough_estimation[i] > 0.4:
            good.append(i)
    # print("the catagory of which recall > 60%")
    # print(good)
    # #[10, 15, 19, 23, 28, 33, 41, 42] 只有10、15、19是重点类
    # quite_good = []
    # for i in range(rough_estimation.size):
    #     if rough_estimation[i] > 0.8:
    #         good.append(i)
    # print("the catagory of which recall > 80%")
    # print(quite_good)



    
