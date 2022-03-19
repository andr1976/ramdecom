from ramdecom import wavespeed
from matplotlib import pyplot as plt
from CoolProp import CoolProp as CP
import pandas as pd
import numpy as np

exp = pd.read_csv(r'..\validation\mixture.csv', sep=';')
input ={}
input['eos'] = 'REFPROP' 
#input['refprop_option'] = 'GERG'
color = ['red','blue','black','green','cyan','grey'] + ['red','blue','black','green','cyan','grey'] 

plt.figure(1)
for index, row in exp.iterrows():
    if index == 1:
        input['pressure'] = row['P (bar)'] * 1e5
        input['temperature'] = row['T (C)'] + 273.15
        input['fluid'] = row['Fluid']
        input['pressure_step'] = 1e5
        input['pressure_break'] = 1e5

        ws = wavespeed.WaveSpeed(input)    
        ws.run()
        filename = "..\\validation\\"  + row['File']
        data = np.loadtxt(filename, delimiter='\t')
        plt.plot(ws.W,ws.P,color = color[index], label=row['Source']+row['Exp. No. '])
        plt.plot(data[:,0],data[:,1]*1e5,'o', color = color[index])
plt.xlabel("Decompression wavespeed (m/s)")
plt.ylabel("Presseure (Pa)")
plt.legend(loc='best')

plt.figure(2)
# for index, row in exp.iterrows():
#     input['pressure'] = row['P (bar)'] * 1e5
#     input['temperature'] = row['T (C)'] + 273.15
#     ws = wavespeed.WaveSpeed(input)    
#     ws.run()
#     plt.plot(ws.T,ws.P,color = color[index], label=row['Source']+row['Exp No.'])

# plt.xlabel("Temperature ($^\circ$C)")
# plt.ylabel("Presseure (Pa)")
# plt.legend(loc='best')
plt.show()
