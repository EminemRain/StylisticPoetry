# -*- coding: utf-8 -*-
import numpy as np
import pickle
class Yun():

    def __init__(self):
        print("loading YunList.txt")
        self.yun_dic = {}
        #self.count = 0
        f = open("data/poemcorpus/YunList.txt",'r')
        lines = f.readlines()

        for line in lines:
            line = line.strip().split(' ')
            for i in range(len(line)):
                line[i] = line[i]
            if line[0] not in self.yun_dic:
                self.yun_dic.update({
                    line[0]:[line[1]]
                    })
            else:
                if not line[1] in self.yun_dic[line[0]]:
                    self.yun_dic[line[0]].append(line[1])

        self.poemyun = {}
        self.mulword_map = {}
        self.word_map = {}

        # please download the pingshui_amb.pkl file from
        #  https://github.com/THUNLP-AIPoet/Datasets/tree/master/CRRD
        #  and then move it into the data/other/ dir
        fyun = open("data/other/pingshui_amb.pkl", "rb")
        self.word_map = pickle.load(fyun,encoding='utf8')
        self.mulword_map = pickle.load(fyun,encoding='utf8')
        self.poemyun = pickle.load(fyun,encoding='utf8')
        fyun.close()


    def getBatchYun(self,batchSen,ivocab, PAD_ID): #return a matrix [none,30+1]
        numLen = len(batchSen)
        numBatch = batchSen[0].shape[0]
        batchYun = np.zeros((numBatch,30+1),dtype='float32')
        for i in range(numBatch):
            tmpsen = []
            for j in range(numLen):
                if j==numLen-1 or j==0 or batchSen[j][i]>=PAD_ID: # go </s>
                    continue
                tmpsen.append(ivocab[batchSen[j][i]])
            #print(tmpsen)
            tmpsen=''.join(tmpsen)
            yun = self.getYun(tmpsen)
            #print(yun)
            if int(yun[0])<0:
                batchYun[i,0] = 1.0
            else:
                batchYun[i,int(yun[0])] = 1.0
        return batchYun

    def getYun(self, sen):
        if sen in self.poemyun:
            return self.poemyun[sen]
        last_word = sen[len(sen)-1]
        if last_word in self.word_map:
            twoword = sen[-2]+sen[-1]
            twoword = twoword
            #print twoword
            if twoword in self.mulword_map:
                return self.mulword_map[twoword]
            threeword = sen[-3]+sen[-2]+sen[-1]
            threeword = threeword
            #print threeword
            if threeword in self.mulword_map:
                return self.mulword_map[threeword]
            #print last_word
            return self.word_map[last_word]
        elif last_word in self.yun_dic:
            return self.yun_dic[last_word]
        else:
            #self.count += 1
            return ['0']

    def updateyun(self, sen, yun):
        def update_mulword(mulword):
            mulword = mulword
            if mulword in self.mulword_map:
                if not yun in self.mulword_map[mulword]:
                    self.mulword_map[mulword].append(yun)
            else:
                self.mulword_map.update({
                    mulword:[yun]
                    })

        word = sen[-1]
        word = word
        yun = yun[0]
        if word in self.yun_map:
            self.yun_map[word][yun] +=1
            twoword = sen[-2]+sen[-1]
            update_mulword(twoword)
            threeword = sen[-3]+sen[-2]+sen[-1]
            update_mulword(threeword)

    def totalpoemlist(self):
        # load the corpus to make sure the model won't generate existing sentences
        f = open("data/poemcorpus/totaljiantipoems_change.txt",'r')
        lines = f.readlines()
        f.close()
        poemyun = {}
        title = ""
        author = ""
        dynasty = ""
        sen_list = []
        count = 0
        for line in lines:
            line = line.strip().split(" ")
            if line[0] == "Title":
                L = len(sen_list)
                yun_list = []
                for i in range(L):
                    yun_list.append(self.getYun(sen_list[i]))
                if L>=1:
                    tmp = yun_list[1]
                    for i in range(L/2):
                        tmp = [val for val in tmp if val in yun_list[i*2+1]]
                else:
                    tmp = []

                if len(tmp) > 1:
                    tmp = [val for val in tmp if val in yun_list[0]]
                if len(tmp) == 1 and tmp[0] != "-1": # []:50366  ["-1"]: 7104  25967
                    for i in range(L/2):
                        yun_list[i*2+1] = tmp
                        self.updateyun(sen_list[i*2+1],tmp)
                    tmp = [val for val in tmp if val in yun_list[0]]
                    if len(tmp)>0:
                        yun_list[0] = tmp
                        self.updateyun(sen_list[0],tmp)

                for i in range(L):
                    poemyun.update({
                        sen_list[i]:yun_list[i]
                        })

                sen_list = []
            else:
                sen_list.append(line[0])

        self.poemyun = poemyun

if __name__ == "__main__":
    yun = Yun()

