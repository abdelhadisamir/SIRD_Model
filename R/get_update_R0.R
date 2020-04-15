# -*- coding: utf-8 -*-
#Created on  Mon Apr 13 14:01:58 2020

#@author: yuqi wang 

library(readxl)
library(R0)
library(MASS)
require('openxlsx')

setwd(".")#当前文件路径
setwd("R/data")#璁剧疆R0鏁版嵁璺緞
R0path = paste(getwd(),"R0_input.xls", sep = "/")
data = read_excel(R0path,sheet=1,na="NA")
num = nrow(data)

diagnosis = data[2]#tail(data, num)[2]#新增确诊数

t_seq = as.Date(as.character(data[[1]]))
firstdate = as.Date(as.character(data[[1]][1]))

mGT<-generation.time("gamma",c(3,1.5))
vals=c(1,2)
r0ml = 0
r0eg =0
for(v in vals){
  if(v==1){
    print("loading ML method")
    c = est.R0.ML(as.double(diagnosis[[1]]),mGT,t=1:length(t_seq),begin=1,end=7 ,date.first.obs=firstdate, time.step=1)
    r0ml=c$R
    print(r0ml)
    #r0ml=append(r0ml,paste(c$conf.int[2],"-",c$conf.int[1]))
    #r0ml=append(r0ml,(c$conf.int[2]-c$conf.int[1])/2)
  } else if(v==2){
    print("loading EG method")
    c = est.R0.EG(as.double(diagnosis[[1]]),mGT,t=1:length(t_seq),begin=1,end=7 ,date.first.obs=firstdate, time.step=1)
    r0eg=c$R
    print(r0eg)
    #r0eg=append(r0eg,paste(c$conf.int[2],"-",c$conf.int[1]))
    #r0eg=append(r0eg,(c$conf.int[2]-c$conf.int[1])/2)
  }
   
}

r0_result_R <- function(r0ml,r0eg) {
  result <- (r0ml +r0eg )/2
  return(result)
}
print(r0_result_R(r0ml,r0eg))
#source('get_update_R0.R')


