# -*- coding: utf-8 -*-

'''
 Created by Overlord Yuan at 2020/02/12
预测主程序
'''
'''导入模型及相关库'''
import os
import pandas as pd
import datetime
# from  SEIR_model import SEIR
from  SIR_model import SIR
from get_day_of_day import get_day_of_day
import matplotlib.pyplot as plt

'''设置当前时间'''
time = get_day_of_day(0).strftime("%Y%m%d")

'''获取数据存储路径'''
# data_path =  'input/2019-nCoV-'+time+'.xlsx'
data_path = 'input/2019-nCoV-0408.xlsx'
R_path = "C:\Program Files\R\R-3.6.3\\bin\\Rscript"
R0_path = 'R/data/R0_result.xls'

def get_data(name = '美国'):
    '''
    获取指定国家数据
    :param name:
    :return:
    '''
    Confirmed_df = pd.DataFrame(pd.read_excel(data_path, sheet_name='每日累计确诊',index_col=0))
    death_df = pd.DataFrame(pd.read_excel(data_path, sheet_name='每日累计死亡',index_col=0))
    recover_df = pd.DataFrame(pd.read_excel(data_path, sheet_name='每日累计治愈', index_col=0))

    Confirmed_data = Confirmed_df[[name]]
    Confirmed_data ['cut'] = Confirmed_data [name].shift(1)
    # Confirmed_data = Confirmed_data.tail(14,7)
    Confirmed_data = pd.DataFrame(Confirmed_data)[-7:]
    Confirmed_cut = pd.DataFrame(Confirmed_data[name] - Confirmed_data["cut"])
    # Confirmed_cut.to_excel('R/data/R0_input.xls')
    Confirmed = Confirmed_df[name].tail(1).tolist()[0]

    # Confirmed = Confirmed_df[name][-1].tolist()

    death = death_df[name][-2:].tolist()
    recover = recover_df[name][-2:].tolist()

    # death = death_list[1]-death_list[0]
    N = Confirmed_df[name].head(1).tolist()[0]

    start_time = list(Confirmed_cut.index)[-2] + datetime.timedelta(days=1)

    return Confirmed,death,Confirmed_cut,N,start_time,recover

def save_data(Diagnosis,increase,name,start_time):
    time = []
    for i in range(len(Diagnosis)):
        time.append((start_time+datetime.timedelta(days=i+1)).strftime("%Y-%m-%d"))
    data = pd.DataFrame({"时间":time,"累计确诊":Diagnosis,"新增确诊":increase})
    '''数据保存'''
    data.to_excel('output/'+name+'-LongForecast-'+start_time.strftime("%Y%m%d")+'.xls')

def main(name):
    Confirmed,death,R0,N,start_time,recover = get_data(name)
    print(start_time)
    # model = SEIR(N=N,E_data=Confirmed*10,I_data=Confirmed,R_data=1,D_data=death,R0=R0,T=7)
    model = SIR(R0,N=N,I_data=Confirmed, R_data=27039, D_data=death, T=7)
    Diagnosis, increase = model.run_Forecast()
    save_data(Diagnosis,increase,name,start_time)

if __name__ == '__main__':
    # name = '西班牙'
    name = '美国'
    # name = '伊朗伊斯兰共和国'
    Confirmed_df = pd.DataFrame(pd.read_excel(data_path, sheet_name='每日累计确诊',index_col=0))
    Confirmed_data = Confirmed_df[name].tolist()[50:]
    time_list =  list(map(lambda x:x.strftime("%Y-%m-%d"),list(Confirmed_df.index)[50:]))
    real_data = [461400,496500,526400,555300]#美国
    # real_data = [152446, 157022,161852,166019]  # 西班牙
    # real_data = [66220, 68192,70029,71686] # '伊朗伊斯兰共和国'
    real_data = Confirmed_data + real_data
    # name = '伊朗伊斯兰共和国'
    Confirmed, death, R0, N,start_time,recover = get_data(name)
    print(start_time)
    # model = SEIR(N=N,E_data=Confirmed*10,I_data=Confirmed,R_data=1,D_data=death,R0=R0,T=7)
    model = SIR(R0,death,recover,N=N,I_data=Confirmed, T=4)
    Diagnosis, increase = model.run_Forecast()

    save_data(Diagnosis, increase,name,start_time)

    # time = []
    for i in range(len(Diagnosis)):
        time_list.append((start_time + datetime.timedelta(days=i + 1)).strftime("%Y-%m-%d"))
    time_list = list(map(lambda x:str(x),time_list))
    # plt.plot(time_list, real_data, color='red', label='真实确诊人数', marker='.')
    # print(time_list[:-4])
    plt.plot(time_list, real_data, color='blue', label='真实确诊人数', marker='.')
    # plt.plot(time_list[:-4], Confirmed_data, color='blue', label='真实确诊人数', marker='.')
    plt.plot(time_list[-4:], Diagnosis, color='Red', label='预测确诊人数',marker = 'D',linewidth=3,ls=":",markerfacecolor='none')
    plt.title(name+'地区确诊人数预测')
    xticks = list(range(0, len(time_list), 5))  # 这里设置的是x轴点的位置
    xlabels = [time_list[x] for x in xticks]  # 这里设置X轴上的点对应那个totalseed中的值
    plt.xticks(xlabels, rotation=30)
    plt.legend()
    plt.grid()
    plt.show()








