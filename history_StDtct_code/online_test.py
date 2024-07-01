import torch
import torch.nn as nn
import glob
import json
import numpy as np
import logging

from one_fc_learning import LSTM, FC
from HuaweiLoader import HuaweiLoader
from pAP import pmAP, dpAP


if __name__ == "__main__":
    net = nn.DataParallel(FC().cuda())
    checkpoint = torch.load("./save_models/mAP_CNN_6.pth")
    net.load_state_dict(checkpoint['model_state_dict'])
    optimizer = torch.optim.SGD(net.parameters(), lr=0.001, momentum=0.9)

    logging.basicConfig(level=logging.DEBUG,
        filename='online_test.log',
        filemode='a'
    )
    train_video_folder = '/opt/data/private/HuaWei/ts-features/ts-features_6/'
    train_txt = '/opt/data/private/HuaWei/data.json'
    with open(train_txt, 'r') as f:
        data = json.load(f)['videos']

    offset = [0.5*30, 1*30, 1.5*30] # second * f/s, no smaller than chunk length
    total = 0 #number of test video
    detection = []
    labels = []
    labels_for_print = [] #
    c_ts = []
    c_ts_for_print = [] #
    in_time = [[], [], []]
    in_time_for_print = [[], [], []] #
    with torch.no_grad():
        for vid in data.keys(): #go through all the test video
            if data[vid]['subset'] != 'test':
                continue
            total += 1
            start = data[vid]['start']
            end = data[vid]['end']
            npy_paths = sorted(glob.glob(train_video_folder+vid[:-7]+'/'+vid+'/*'))

            c_tminus1 = 0
            for npy in npy_paths: #go through all the chunks
                ip = torch.from_numpy(np.load(npy)).cuda()
                output = net(ip)
                c_t = torch.max(output.data, 1).indices

                #Got a detection if meet the two conditions
                if c_t != 0 and c_t != c_tminus1:
                    detection.append(output.squeeze().cpu().numpy().tolist())
                    c_ts.append(c_t.cpu().numpy()[0])
                    c_ts_for_print.append(c_t.cpu().numpy()[0])
                    
                    index = int(npy[-10:-4])
                    frm_last = index * 6
                    if frm_last >= start and frm_last <= end:
                        labels.append(data[vid]['label'])
                        labels_for_print.append(data[vid]['label'])                        
                    else:
                        labels.append(0)
                        labels_for_print.append(0)
                    
                    temp1 = abs((index-1)*6+1 - start) #chunk start - true start
                    temp2 = abs(index*6 - start) #chunk end - true start
                    if temp1 < offset[0] or temp2 < offset[0]:
                        in_time[0].append(True)
                        in_time_for_print[0].append(True)
                    else:
                        in_time[0].append(False)
                        in_time_for_print[0].append(False)
                    if temp1 < offset[1] or temp2 < offset[1]:
                        in_time[1].append(True)
                        in_time_for_print[1].append(True)
                    else:
                        in_time[1].append(False)
                        in_time_for_print[1].append(False)
                    if temp1 < offset[2] or temp2 < offset[2]:
                        in_time[2].append(True)
                        in_time_for_print[2].append(True)
                    else:
                        in_time[2].append(False)
                        in_time_for_print[2].append(False)

                c_tminus1 = c_t

            if total % 20 == 0:
                logging.info("Labels: "+np.array2string(np.array(labels_for_print)))
                logging.info("C_ts: "+np.array2string(np.array(c_ts_for_print)))
                logging.info("In time: "+np.array2string(np.array(in_time_for_print)))
                labels_for_print = [] #
                c_ts_for_print = [] #
                in_time_for_print = [[], [], []] #
        
    
    #Metric 1: Acc
    print('Total:', total) #2879
    correct0 = correct1 = correct2 = 0
    for i in range(len(in_time[0])):
        if c_ts[i] == labels[i] and in_time[0][i]:
            correct0 += 1
        if c_ts[i] == labels[i] and in_time[1][i]:
            correct1 += 1
        if c_ts[i] == labels[i] and in_time[2][i]:
            correct2 += 1
    acc0 = correct0 / total
    acc1 = correct1 / total
    acc2 = correct2 / total
    print('Acc:', acc0, acc1, acc2)

    #Metric 2: FPPV, can be transformed into metirc 1
    # FP = total - correct
    # FPPV = FP / total
    # print('FPPV:', FPPV)

    #Metric 3: p-mAP
    one_hot_labels = torch.zeros(len(labels), 46).scatter_(1, torch.tensor(np.expand_dims(labels, 1)), 1.)
    pmap = pmAP(torch.tensor(detection), one_hot_labels, np.array(in_time))
    print('pmap:', pmap)

    #Metric 4: d-pAP
    depth = np.around(np.arange(0.1, 1.1, 0.1), 1).tolist()
    dpap = dpAP(depth, torch.tensor(detection), one_hot_labels, np.array(in_time))
    print('pmap:', dpap)
