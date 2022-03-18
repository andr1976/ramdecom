from ramdecom import wavespeed
from matplotlib import pyplot as plt
import pandas as pd
import numpy as np

exp = pd.read_csv(r'..\validation\pure.csv', sep=';')
input ={}
input['eos'] = 'HEOS' 
input['fluid'] = 'CO2'
color = ['red','blue','black','green','cyan','grey']
plt.figure(1)
for index, row in exp.iterrows():
    input['pressure'] = row['P (bar)'] * 1e5
    input['temperature'] = row['T (C)'] + 273.15
    ws = wavespeed.WaveSpeed(input)    
    ws.run()
    filename = "..\\validation\\"  + row['File']
    data = np.loadtxt(filename, delimiter='\t')
    plt.semilogy(ws.W,ws.P,color = color[index], label=row['Source']+row['Exp No.'])
    plt.semilogy(data[:,0],data[:,1]*1e5,'o', color = color[index])
plt.legend(loc='best')

plt.figure(2)
for index, row in exp.iterrows():
    input['pressure'] = row['P (bar)'] * 1e5
    input['temperature'] = row['T (C)'] + 273.15
    ws = wavespeed.WaveSpeed(input)    
    ws.run()
    plt.plot(ws.T,ws.P,color = color[index], label=row['Source']+row['Exp No.'])
plt.legend(loc='best')
plt.show()
