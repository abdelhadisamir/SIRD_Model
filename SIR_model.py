# -*- coding: utf-8 -*-
'''
 Created by Overlord Yuan at 2020/04/13
模型程序
'''
import os
import numpy as np
import pandas as pd
import subprocess
import datetime
import scipy.integrate as spi
import matplotlib.pyplot as plt
from tqdm import tqdm
from get_day_of_day import get_day_of_day
plt.rcParams['font.sans-serif'] = ['SimHei'] # 步骤一（替换sans-serif字体）
plt.rcParams['axes.unicode_minus'] = False
# INI = (S_0,I_0,E_0,R_0)

'''设置当前时间'''
time = get_day_of_day(0).strftime("%Y%m%d")

'''获取数据存储路径'''
# data_path =  'input/2019-nCoV-'+time+'.xlsx'
data_path = 'input/2019-nCoV-0408.xlsx'
R_path = "C:\Program Files\R\R-3.6.3\\bin\\Rscript"
R0_path = 'R/data/R0_result.xls'

class SIR():
    def __init__(self,ins_data,D_data,R_data,N=100000,I_data=1,T = 10):
        '''
        SIR预测模型
        :param R0_data: 近7天新增确诊数
        :param N: 地区口总数
        :param I_data: 感染个体总数
        :param R_data: 治愈个体总数
        :param D_data: 死亡个体总数
        :param T: 预测天数
        '''
        self.ins_7 = ins_data
        # R0为基本传染数
        self.R0 = self.run_R(ins_data)
        # N为预测天数
        self.T = T
        # N为地区口总数
        self.N = N
        # I_0为现存感染个体的初始比例
        self.I_0 = (I_data-R_data[1]-D_data[1]) / N
         # R_0为治愈个体的初始比例
        self.R_0 = R_data[1] / N
        # D_0为死亡个体的初始比例
        self.D_0 = D_data[1] / N
        # S_0为易感个体的初始比例
        self.S_0 = 1 - self.I_0 - self.R_0 - self.D_0
        # gamma为感染者治愈率
        self.gamma = (R_data[1] -R_data[0])/ (I_data-R_data[1]-D_data[1])
        # self.ga = R_data[1] /I_data
        # self.ga = 0.04
        # mortality为死亡率
        self.mortality = (D_data[1]-D_data[0]) / (I_data-R_data[1]-D_data[1])
        # self.m = D_data[1] / I_data
        self.m = (min(D_data[1]/I_data,0.06) + 0.06)/2
        # β为疾病传播概率
        self.beta = self.R0 * (self.m)

        '''参数汇总'''
        c = []
        c.append(self.N) # 地区口总数
        c.append(round(self.S_0 * N)) # 易感个体总数
        c.append(I_data) # 感染个体总数
        c.append(R_data) # 治愈总数
        c.append(self.R0) # 基本传染系数
        c.append(self.beta) # 疾病传播概率
        c.append(self.gamma) # 疑似者排除治愈率
        c.append(self.mortality)  # 疑似者排除治愈率

    def run_R(self,data):
        '''
        计算基本传染数
        :return:
        '''
        data.to_excel('R/data/R0_input.xls')
        print("----------------------------------------------------")
        print("运行R程序")
        program_path = os.path.join(os.path.abspath(os.path.join(os.getcwd(), ".")), "R/get_update_R0_v1.R")
        print(program_path)
        # path = R_path+" "+program_path
        subprocess.call([R_path, program_path])
        print("R程序运行结束。")
        print("----------------------------------------------------")
        R0 = list(pd.read_excel(R0_path).columns)[0]
        print(R0)
        return R0
    # def _funcSIRD(self,prop,_):
    #     '''SIR模型'''
    #     Y = np.zeros(8)
    #     X = prop
    #     # 易感个体变化
    #     Y[0] = -X[5]*X[0]
    #     # 感染个体变化
    #     Y[1] = X[5]*X[0]*X[1]
    #     # 治愈个体变化
    #     Y[2] = X[4]*X[1]
    #     Y[3] = X[1]*X[6]
    #
    #     return Y

    def funcSIRD(self, prop, _):
        '''SIR模型'''
        Y = np.zeros(4)
        X = prop
        # 易感个体变化
        Y[0] = -self.beta * X[0]* X[1]
        # 感染个体变化
        Y[1] = self.beta * X[0] * X[1]-self.gamma * X[1]-self.mortality * X[1]
        # 治愈个体变化
        Y[2] = self.gamma * X[1]
        # 死亡个体变化
        Y[3] =self.mortality * X[1]

        return Y

    def updata_ins(self,new_ins):
        old_data = sum(new_ins[0][1:])
        new_data =  sum(new_ins[1][1:])
        ins = round((new_data-old_data)*self.N)
        index_ind = list(self.ins_7.index)[-1]+datetime.timedelta(days=1)
        self.ins_7.loc[ index_ind] = ins
        self.ins_7 = self.ins_7.tail(7)

    def run_Forecast(self):
        '''
        :return: 预测结果、新增结果
        '''
        for i in tqdm(range(self.T)):
            T_range = np.arange(0, 2)
            if i == 0:
                INI = (self.S_0,self.I_0,self.R_0,self.D_0)
                RES =  spi.odeint(self.funcSIRD,INI,T_range).tolist()
            else:
                # 更新痊愈率
                self.gamma = (RES[-1][2]-RES[-2][2])/RES[-1][1]
                # 更新死亡率
                self.mortality = (RES[-1][3]-RES[-2][3])/RES[-1][1]
                # 更新R0
                self.updata_ins(RES[-2:])
                self.R0 = self.run_R(self.ins_7)
                self.m =  (min((RES[-1][3])/sum(RES[-1][1:]),0.06)+0.06)/2
                self.beta = self.R0 * (self.m)
                INI = (RES[-1][0], RES[-1][1], RES[-1][2], RES[-1][3])
                temp = spi.odeint(self.funcSIRD,INI,T_range).tolist()[-1]
                RES.append(temp)

        RES = np.array(RES) * self.N
        '''确诊人数'''
        Diagnosis = list(map(lambda x,y,z: round(x+y+z), RES[:, 1].tolist(),RES[:, 2].tolist(),RES[:, 3].tolist()))
        '''新增人数'''
        increase = []
        # temp = RES[:, 1]
        for i in range(self.T + 1):
            if (i == 0):
                continue
            else:
                increase.append(round(( Diagnosis[i] -  Diagnosis[i - 1])))
        return Diagnosis[1:],increase




