from ramdecom import wavespeed
from matplotlib import pyplot as plt
from CoolProp import CoolProp as CP
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
    if index == 3:
        input['extrapolate'] = True
    ws = wavespeed.WaveSpeed(input)    
    ws.run()
    filename = "..\\validation\\"  + row['File']
    data = np.loadtxt(filename, delimiter='\t')
    plt.semilogy(ws.W,ws.P,color = color[index], label=row['Source']+row['Exp No.'])
    plt.semilogy(data[:,0],data[:,1]*1e5,'o', color = color[index])
plt.xlabel("Decompression wavespeed (m/s)")
plt.ylabel("Presseure (Pa)")
plt.legend(loc='best')

plt.figure(2)
for index, row in exp.iterrows():
    input['pressure'] = row['P (bar)'] * 1e5
    input['temperature'] = row['T (C)'] + 273.15
    ws = wavespeed.WaveSpeed(input)    
    ws.run()
    plt.plot(ws.T,ws.P,color = color[index], label=row['Source']+row['Exp No.'])

pc = ws.asfluid.keyed_output(CP.iP_critical)
Tc = ws.asfluid.keyed_output(CP.iT_critical)
Tt = ws.asfluid.keyed_output(CP.iT_triple)
pt = ws.asfluid.keyed_output(CP.iP_triple)

Ts = np.linspace(Tt, Tc, 100)
ps = CP.PropsSI('P', 'T', Ts, 'Q', 0, 'CO2')

plt.plot(Ts, ps, '--', color='dimgrey', label='Saturation line')
plt.plot(Tc, pc, 'ko', label='Critical point')
plt.plot(Tt, pt, linestyle='none', marker='o', color='black', fillstyle='none', label='Triple point')
plt.xlabel("Temperature ($^\circ$C)")
plt.ylabel("Presseure (Pa)")
plt.legend(loc='best')
plt.show()
