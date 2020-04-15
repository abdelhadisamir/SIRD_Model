#author: ywang
#author:Overlord.Y
#updated time:20200208

library(readxl)
library(R0)
require('openxlsx')

##设置参数
num=7

###读取上一次数据
print("read lasted data")
setwd(".")#获取当前路径
#setwd("data/R0_data")#设置R0数据路径
R0path = paste(getwd(),"data/R0_data", sep = "/")#获取R0数据路径
print(R0path)#输出R0数据路径
day = Sys.Date()#获取当天日期
#获取前一天R0数据文件名称
file_name = paste("R0",paste(format(day-1,format="%Y%m%d"),"xlsx", sep = "."),sep="-")
print(paste(R0path,file_name, sep = "/"))
wb = read_excel(na="NA",path=paste(R0path,file_name, sep = "/"),sheet = 1)
wb2 =  read_excel(na="NA",path=paste(R0path,file_name, sep = "/"),sheet = 2)
#read.xls(",sheet=1,na.strings=c("NA","#DIV/0!"))
#读取每日更新数据
print("read daily updated data")
Ipath = paste(getwd(),"data/I_data", sep = "/")#获取每日更新数据路径
I_file_name = paste("2019-nCoV",paste(format(day,format="%Y%m%d"),"xlsx", sep = "."),sep="-")
filepath = paste(Ipath,I_file_name, sep = "/")
wuhan = read_excel(path=filepath,sheet=1,na="NA")
print(1)
wuhan_data = tail(wuhan,num)
hubei_data = tail(read_excel(path=filepath,sheet=2,na="NA")[13],num)
hubei_no_wuhan = hubei_data-wuhan_data[5]
china_data = tail(read_excel(path=filepath,sheet=3,na="NA")[10],num)
china_no_hubei = china_data-hubei_data
wuhan_up_data = wuhan_data[5]
#names(wuhan_up_data) = tail(wuhan[1],10)
#names(hubei_no_wuhan) = tail(wuhan[1],10)
#names(china_no_hubei) = tail(wuhan[1],10)

#R0计算
print("get updated R0 value with range")
r0ml=list(as.character(tail(wuhan_data[[1]],1)))
print(r0ml)
r0eg=list(as.character(tail(wuhan_data[[1]],1)))
firstdate = as.Date(as.character(wuhan_data[[1]][1]))
mGT<-generation.time("gamma",c(3,1.5))
vals=c(1,2,3)
print("loading ML method")

t_seq = as.Date(as.character(wuhan_data[[1]]))
for(v in vals){
  if(v==1){
    c = est.R0.ML(as.double(wuhan_up_data[[1]]),mGT,t=1:length(t_seq),begin=1,end=num,date.first.obs=firstdate, time.step=1)
    r0ml=append(r0ml,c$R)
    r0ml=append(r0ml,paste(c$conf.int[2],"-",c$conf.int[1]))
    r0ml=append(r0ml,(c$conf.int[2]-c$conf.int[1])/2)
  } else if(v==2){
    c = est.R0.ML(as.double(hubei_no_wuhan[[1]]),mGT,t=1:length(t_seq),begin=1,end=num,date.first.obs=firstdate, time.step=1)
    r0ml=append(r0ml,c$R)
    r0ml=append(r0ml,paste(c$conf.int[2],"-",c$conf.int[1]))
    r0ml=append(r0ml,(c$conf.int[2]-c$conf.int[1])/2)
  }else if (v==3){
    c = est.R0.ML(as.double(china_no_hubei[[1]]),mGT,t=1:length(t_seq), begin=1,end=num,date.first.obs=firstdate, time.step=1)
    r0ml=append(r0ml,c$R)
    r0ml=append(r0ml,paste(c$conf.int[2],"-",c$conf.int[1]))
    r0ml=append(r0ml,(c$conf.int[2]-c$conf.int[1])/2)
  }
}
print("loading EG method")
for(v in vals){
  if(v==1){
    c = est.R0.EG(as.double(wuhan_up_data[[1]]),mGT,t=1:length(t_seq),begin=1,end=num,date.first.obs=firstdate, time.step=1)
    r0eg=append(r0eg,c$R)
    r0eg=append(r0eg,paste(c$conf.int[2],"-",c$conf.int[1]))
    r0eg=append(r0eg,(c$conf.int[2]-c$conf.int[1])/2)
  } else if(v==2){
    c = est.R0.EG(as.double(hubei_no_wuhan[[1]]),mGT,t=1:length(t_seq),begin=1,end=num,date.first.obs=firstdate, time.step=1)
    r0eg=append(r0eg,c$R)
    r0eg=append(r0eg,paste(c$conf.int[2],"-",c$conf.int[1]))
    r0eg=append(r0eg,(c$conf.int[2]-c$conf.int[1])/2)
  }else if (v==3){
    c = est.R0.EG(as.double(china_no_hubei[[1]]),mGT,t=1:length(t_seq),begin=1,end=num,date.first.obs=firstdate, time.step=1)
    r0eg=append(r0eg,c$R)
    r0eg=append(r0eg,paste(c$conf.int[2],"-",c$conf.int[1]))
    r0eg=append(r0eg,(c$conf.int[2]-c$conf.int[1])/2)
  }

}
print("processing dataframe")
df_r0ml = data.frame(r0ml)
# colnames(df_r0ml)<- c("date",'武汉-r0',"武汉ro-range","武汉-errorbar","湖北除武汉-r0","湖北除武汉ro-range","湖北除武汉-errorbar","全国除湖北-r0","全国除湖北ro-range","全国除湖北-errorbar")
colnames(df_r0ml) = colnames(wb)
df_r0eg = data.frame(r0eg)
colnames(df_r0eg) = colnames(wb)
# colnames(df_r0eg)<- c("date","武汉-r0","武汉ro-range","武汉-errorbar","湖北除武汉-r0","湖北除武汉ro-range","湖北除武汉-errorbar","全国除湖北-r0","全国除湖北ro-range","全国除湖北-errorbar")

print("merging dataframe")
bothdfs1 <- rbind(wb,df_r0ml)
bothdfs2 <- rbind(wb2,df_r0eg)

##数据保存XLSX文件
print("saving xlsx file with 2 sheets")
list_of_datasets <- list("R0 ML" = bothdfs1, "R0 EG" = bothdfs2)
#print(list_of_datasets)
file_name = paste("R0",paste(format(day,format="%Y%m%d"),"xlsx", sep = "."),sep="-")
write.xlsx(list_of_datasets, file =paste(R0path,file_name, sep = "/"))
print("数据保存成功")

