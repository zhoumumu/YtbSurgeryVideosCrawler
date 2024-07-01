import numpy as np

# 第一列是样本id，第二列是分类的得分，第三列是ground truth
table = np.array([
[0, 0.23, 0],
[1, 0.76, 1],
[2, 0.01, 0],
[3, 0.91, 1],
[4, 0.13, 0],
[5, 0.45, 0],
[6, 0.12, 1],
[7, 0.03, 0],
[8, 0.38, 1],
[9, 0.11, 0],
[10, 0.03, 0],
[11, 0.09, 0],
[12, 0.65, 0],
[13, 0.07, 0],
[14, 0.12, 0],
[15, 0.24, 1],
[16, 0.1, 0],
[17, 0.23, 0],
[18, 0.46, 0],
[19, 0.08, 1]
])

# 按分数从大到小排
index = np.argsort(table[:,1])[::-1] # id的顺序
T = table[index] #按id顺序重排table
'''
在T表上拦腰划一条的线（依据可以是top-N,也可以是confidence阈值），
线以上为positive，线以下为negative
recall = true positive / 所有正样本数
precision = ture positive / 线上样本总数
'''
"""
N个样本中有M个正例，那么我们会得到M个recall值（1/M, 2/M, ..., M/M）,
对于每个recall值r，我们可以计算出对应（r' > r）的最大precision
然后对这M个precision值取平均即得到最后的AP值
"""
# 补充上述求法中的最大precision：这个最大值总是把线划到第m个true positive样本下面，对应的precision值
# 不需要分别求所有的top-N precision，也不需要求recall

count_TP = 0
precision = []
for i in range(len(T)):
    if(T[i][2] == 1):
        count_TP += 1
        precision.append(count_TP/(i+1))
AP = np.mean(precision)


####################################
####################################



##对于分类，给出三个类别, 七个样本
import torch
target = torch.tensor(np.array([
[0, 0, 1],
[0, 1, 0],
[0, 1, 0],
[1, 0, 0],
[0, 0, 1],
[1, 0, 0],
[0, 1, 0]
]))
output = torch.tensor(np.array([
[0.23, 0.01, 0.76],
[0.91, 0.13, 0.45],
[0.12, 0.03, 0.38],
[0.11, 0.03, 0.09],
[0.65, 0.07, 0.12],
[0.24, 0.10, 0.23],
[0.46, 0.08, 0.17]
]))


#按照每一维排序，分别算得三类AP
AP = []
for i in range(3):
    temp = output[:, i]
    index = temp.argsort(0, descending=True)
    T = target[:, i][index]

    count_TP = 0
    precision = []
    for j in range(len(T)):
        if(T[j] == 1):
            count_TP += 1
            precision.append(count_TP/(j+1))
    AP.append(np.mean(precision))
#print(AP) #right the same with result from API below


import torchnet.meter as tnt

apmeter = tnt.APMeter()
mapmeter = tnt.mAPMeter()
for i in range(7):
    apmeter.add(output[i].unsqueeze(0), target[i].unsqueeze(0))
    mapmeter.add(output[i].unsqueeze(0), target[i].unsqueeze(0))
#print("ap:", apmeter.value()) # ap: tensor([0.2679, 0.7556, 0.6667])
#print("map:", mapmeter.value()) # map: tensor(0.5634)


####################################
####################################


"""
## { function_description }
##
## :type       output:   { torch tensor of size sample*type}
## :param      output:   The output
## :type       target:   { torch tensor of size sample*type with value 0/1 }
## :param      target:   One hot label
## :type       in_time:  { numpy array of size offset*sample with value true/false }
## :param      in_time:  In time
##
## :returns:   { description_of_the_return_value }
## :rtype:     { return_type_description }
"""
def pmAP(output, target, in_time):
    num_type = output.size()[1]
    num_offset = len(in_time)
    pmap = []
    for k in range(num_offset):
        AP = []
        for i in range(num_type):
            temp = output[:, i]
            index = temp.argsort(0, descending=True)
            T = target[:, i][index]
            T1 = in_time[k][index]

            count_TP = 0
            precision = []
            for j in range(len(T)):
                if T[j] == 1 and T1[j]:
                    count_TP += 1
                    precision.append(count_TP/(j+1))
            if count_TP == 0:
                print("!!! TP of type ", i, " is counted as 0 at offset ", k)
                AP.append(0)
            else:
                AP.append(np.mean(precision))
        pmap.append(np.mean(AP))
    return pmap

in_time = np.array([
[True, False, True, False, True, False, True],
[True, False, True, True, True, False, True],
[True, False, True, True, True, True, True]
])
#print(pmAP(output, target, in_time))


"""
## { function_description }
##
## :type       depth:    { numpy array}
## :param      depth:   The depth
## :type       output:   { torch tensor of size sample*type}
## :param      output:   The output
## :type       target:   { torch tensor of size sample*type with value 0/1 }
## :param      target:   One hot label
## :type       in_time:  { numpy array of size offset*sample with value true/false }
## :param      in_time:  In time
##
## :returns:   { description_of_the_return_value }
## :rtype:     { return_type_description }
"""
def dpAP(depth, output, target, in_time):
    num_type = output.size()[1]
    num_offset = (in_time.shape)[0]
    dpap = [] #[, ... ,]for every type, [, ... ,] store point-AP for different depth
    for i in range(num_type):
        temp = output[:, i]
        index = temp.argsort(0, descending=True)
        T = target[:, i][index]

        prs = [] #offset*...
        for k in range(num_offset):
            T1 = in_time[k][index]
            count_TP = 0
            pr = [] #line of precision and recall
            for j in range(len(T)):
                if T[j] == 1 and T1[j]:
                    count_TP += 1
                    pr.append(count_TP/(j+1))
            if pr == []:
                print("!!! TP of type ", i, " is counted as 0 at offset ", k)
            prs.append(pr)

        '''
        Traditional way of 11-point interpolated is not that precise, it take the biggest value as interpolation
        But the precise interpolation is too complex to implement
        Here we got new pr values under required recall depths, and then average in different offsets(different prs)
        '''
        count_1 = len((T==1).tolist()) # number of this type in all the samples, lable as 1
        interpolated_prs = []
        # len(pr) are not always the same, and len(pr) <= count_1,
        # and len(pr) could equal to 0
        for pr in prs:
            if pr == []:
                interpolated_prs.append(np.zeros(len(depth)).tolist())
                continue
            new_pr = []
            temp_p = pr[0]
            n = 0 # idx on pr
            for recall in depth:
                if (n+1)/count_1 < recall: #recall on the position n < recall_this_round
                    temp_p = pr[n] #before moving, temp_p should keep the current p
                    while n < len(pr)-1 and (n+1)/count_1 < recall:
                        n += 1 #move to a position where recall >= required
                if (n+1)/count_1 == recall: #find a precision decline
                    temp_p = pr[n]
                new_pr.append(temp_p)
            interpolated_prs.append(new_pr)
        #print(interpolated_prs)
        dpap.append(np.mean(interpolated_prs, 0))
    
    #print(dpap)
    return np.mean(dpap, 0)

depth = np.around(np.arange(0.1, 1.1, 0.1), 1).tolist()
#print(dpAP(depth, output, target, in_time))


#Test for the interpolation, covering many edge cases
#Is this algorithm complete? I guess so... to figure it out, my hairs almost fallen out
# count_1 = 5
# pr = np.random.randint(10, size=3)
# >>>[0 6 7]
# >>>[0.2 0.4 0.6]
# >>>[0, 0, 0, 6, 6, 7, 7, 7, 7, 7]

# count_1 = 6
# pr = np.random.randint(10, size=3)
# >>>[2 8 8]
# >>>[0.16666667 0.33333333 0.5       ]
# >>>[2, 2, 2, 8, 8, 8, 8, 8, 8, 8]

# count_1 = 10
# pr = np.random.randint(10, size=10)
# >>>[6 0 4 3 1 5 9 5 2 9]
# >>>[0.1 0.2 0.3 0.4 0.5 0.6 0.7 0.8 0.9 1. ]
# >>>[6, 0, 4, 3, 1, 5, 9, 5, 2, 9]

# count_1 = 11
# pr = np.random.randint(10, size=6)
# >>>[0 3 7 4 1 3]
# >>>[0.09090909 0.18181818 0.27272727 0.36363636 0.45454545 0.54545455]
# >>>[0, 3, 7, 4, 1, 3, 3, 3, 3, 3]

# count_1 = 100
# pr = np.random.randint(10, size=90)
# >>>[3 9 1 9 2 3 1 9 7 5
#    4 1 9 8 6 8 4 1 2 1 
#    6 0 5 9 5 8 2 1 0 4 
#    4 7 0 2 6 2 2 5 5 6
#    3 1 0 1 9 5 8 7 3 5
#    1 2 1 2 0 3 8 1 8 8
#    0 2 8 0 2 5 9 7 2 9
#    4 1 2 7 9 2 4 2 2 5
#    9 7 8 8 2 1 7 5 8 9]
# >>>[0.01 0.02 0.03 0.04 0.05 0.06 0.07 0.08 0.09 0.1 0.11 0.12 0.13 0.14
#    0.15 0.16 0.17 0.18 0.19 0.2  0.21 0.22 0.23 0.24 0.25 0.26 0.27 0.28
#    0.29 0.3  0.31 0.32 0.33 0.34 0.35 0.36 0.37 0.38 0.39 0.4  0.41 0.42
#    0.43 0.44 0.45 0.46 0.47 0.48 0.49 0.5  0.51 0.52 0.53 0.54 0.55 0.56
#    0.57 0.58 0.59 0.6  0.61 0.62 0.63 0.64 0.65 0.66 0.67 0.68 0.69 0.7
#    0.71 0.72 0.73 0.74 0.75 0.76 0.77 0.78 0.79 0.8  0.81 0.82 0.83 0.84
#    0.85 0.86 0.87 0.88 0.89 0.9 ]
# >>>[5, 1, 4, 6, 5, 8, 9, 5, 9, 9]


# print(pr)
# print(np.linspace(1/count_1, len(pr)/count_1, len(pr))) #when step is non-integer, arange/range is not that reliable
# depth = np.around(np.arange(0.1, 1.1, 0.1), 1).tolist() #if not round, it gives 0.30000000000000004 at depth[2]
# new_pr = []
# temp_p = pr[0]
# n = 0 # idx on pr
# for recall in depth:
#     if (n+1)/count_1 < recall: #recall on the position n < recall_this_round
#         temp_p = pr[n] #before moving, temp_p should keep the current p
#         while n < len(pr)-1 and (n+1)/count_1 < recall:
#             n += 1 #move to a position where recall >= required
#     if (n+1)/count_1 == recall: #find a precision decline
#         temp_p = pr[n]
#     new_pr.append(temp_p)
# print(new_pr)