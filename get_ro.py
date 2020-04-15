import pandas as pd
import numpy as np

w = pd.DataFrame(pd.read_excel('data/R0.xlsx',sheet_name="sheet1"))
data0 = np.array(w["全国"].tolist())
time = np.array(range(1,5))
# time1 = np.array(range(14,45))

fit = np.polyfit(time, np.log(data0), 1)
print(fit)

