# -*- coding: utf-8 -*-
'''
 Created by Overlord Yuan at 2020/04/13
模型程序
'''
import scipy.integrate as spi
import numpy as np
import matplotlib.pyplot as plt
from get_day_of_day import get_day_of_day
plt.rcParams['font.sans-serif'] = ['SimHei'] # 步骤一（替换sans-serif字体）
plt.rcParams['axes.unicode_minus'] = False
# INI = (S_0,I_0,E_0,R_0)

class SEIR():
    def __init__(self,N=100000,E_data=1,I_data=1,R_data=41832,D_data =1,R0=2,u = 0.007,T = 10):
        self.T = T
        # N为地区口总数
        self.N = N
        # I_0为感染个体的初始比例
        self.I_0 = I_data / N
        # E_0为疑似个体的初始比例
        self.E_0 = E_data / N
        # R_0为治愈个体的初始比例
        self.R_0 = R_data / N
        # D_0为死亡个体的初始比例
        self.D_0 = D_data / N
        # S_0为易感个体的初始比例
        self.S_0 = 1 - self.I_0 - self.E_0 - self.R_0 - self.D_0
        # gamma_1为潜伏期治愈率
        # gamma_2为感染者治愈率
        self.gamma_2 = R_data / I_data
        self.gamma_1 = 0
        # alpha为潜伏期发展为患者的比例
        self.alpha = 0.4
        # β为疾病传播概率
        self.beta = R0 * self.gamma_2
        # mortality为死亡率
        self.mortality = D_data / I_data

        '''参数汇总'''
        c = []
        c.append(self.N) # 地区口总数
        c.append(round(self.S_0 * N)) # 易感个体总数
        c.append(E_data)# 疑似个体总数
        c.append(I_data) # 感染个体总数
        c.append(R_data) # 治愈总数
        c.append(D_data)  # 死亡总数
        c.append(R0) # 基本传染系数
        c.append(self.alpha) #疑似者发展为患者的比例
        c.append(self.beta) #疾病传播概率
        c.append(self.gamma_2) #疑似者排除治愈率
        c.append(self.mortality) #死亡率

    def funcSEIRD(self,prop,_):
        '''SEIRD模型'''
        Y = np.zeros(8)
        X = prop
        # 易感个体变化
        Y[0] = -X[0]*X[6]
        # 感染个体变化
        Y[1] = self.alpha * X[2]
        # 疑似期个体变化
        Y[2] = X[6] * X[0] * X[1] - (self.alpha + self.gamma_1) * X[2]
        # 治愈个体变化
        Y[3] = X[5] * X[1]
        # 死亡个体变化
        Y[4] = X[7] * X[1]
        return Y

    def run_Forecast(self):
        '''
        :return: 预测结果、新增结果
        '''
        for i in range(self.T):
            T_range = np.arange(0, 2)
            if i == 0:
                INI = (self.S_0,self.I_0,self.E_0,self.R_0,self.D_0,self.gamma_2,self.beta,self.mortality)
                RES =  spi.odeint(self.funcSEIRD,INI,T_range).tolist()
            else:
                gamma_2 = RES[-1][3]/RES[-1][1]
                mortality = RES[-1][4]/RES[-1][1]
                INI = (RES[-1][0], RES[-1][1], RES[-1][2], RES[-1][3],RES[-1][4], gamma_2,self.beta,mortality )
                temp = spi.odeint(self.funcSEIRD,INI,T_range).tolist()[-1]
                RES.append(temp)

        RES = np.array(RES) * self.N

        '''新增人数'''
        increase = []

        temp = RES[:, 1]
        for i in range(self.T + 1):
            if (i == 0):
                continue
            else:
                increase.append(round((temp[i] - temp[i - 1])))
        '''确诊人数'''
        Diagnosis = list(map(lambda x:round(x),RES[:, 1].tolist()))[0:-1]
        return Diagnosis,increase




