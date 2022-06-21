# RAMDECOM
# Copyright (c) 2022 Anders Andreasen
# Published under an MIT license

import streamlit as st
import pandas as pd
from PIL import Image
import base64
import matplotlib.pyplot as plt 
from CoolProp import CoolProp as CP
import numpy as np

try:
    import wavespeed
except:
    import sys
    import os
    #ramdecom_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "..", "ramdecom")
    ramdecom_path = os.path.join(os.path.abspath(os.getcwd()), "..", "ramdecom")
    sys.path.append(os.path.abspath(ramdecom_path))
    from ramdecom import wavespeed


def get_table_download_link(df, filename):
    """
    Generates a link allowing the data in a given panda dataframe to be downloaded
    in:  dataframe
    out: href string
    """
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # some strings <-> bytes conversions necessary here
    filename = filename+'.csv'
    return f'<a href="data:application/octet-stream;base64,{b64}" download={filename}>Download csv file</a>'


def read_input():
    sideb = st.sidebar

    with sideb:
        #try:
        #    image_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "..", "docs", "img", "Sketch.png")
        #     icon = Image.open(image_path)
        #     st.image(icon, use_column_width=True, caption="HydDown")
        # except:
        #     pass

        with st.form(key='my_form'):
             submit_button = st.form_submit_button(label='Run calculation')
             temp = float(st.text_input('Initial temp. (C):', 25))
             pres = float(st.text_input('Initial pressure (bar):', 150.))
        
    input = {}
    input['temperature'] = 273.15 + temp
    input['pressure'] = pres * 1e5
    input['eos'] = 'HEOS'
    input['fluid'] = 'CO2'
    return input

if __name__ == "__main__":
    st.set_page_config(layout='wide')

    input = read_input()
    ws = wavespeed.WaveSpeed(input)

    with st.spinner('Calculating, please wait....'):
        ws.run()

    st.title('Pure CO2 pipeline decompression wavespeed')
    st.subheader(r'https://github.com/andr1976/ramdecom')
    my_expander = st.expander("Description")

    my_expander.write('Calculation of decompression wavespeed using the CoolProp library. Results to be used in combination with e.g. the Battelle two-curve method.')

    df = ws.get_dataframe()
    file_name = st.text_input('Filename for saving data:', 'saved_data') 
    
    st.markdown(get_table_download_link(df, file_name), unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    fig, ax = plt.subplots()

    ax.plot(ws.W, ws.P, 'k', label="Calculated")
    ax.legend(loc='best')
    ax.set_xlabel("Decompression wave speed (m/s)")
    ax.set_ylabel("Pressure (Pa)")
    
    col1.pyplot(fig)


    fig1, ax1 = plt.subplots()
    ax1.plot(ws.T,ws.P,'k',label='Decompression path')

    pc = ws.asfluid.keyed_output(CP.iP_critical)
    Tc = ws.asfluid.keyed_output(CP.iT_critical)
    Tt = ws.asfluid.keyed_output(CP.iT_triple)
    pt = ws.asfluid.keyed_output(CP.iP_triple)

    Ts = np.linspace(Tt, Tc, 100)
    ps = CP.PropsSI('P', 'T', Ts, 'Q', 0, 'CO2')

    ax1.plot(Ts, ps, '--', color='dimgrey', label='Saturation line')
    ax1.plot(Tc, pc, 'ko', label='Critical point')
    ax1.plot(Tt, pt, linestyle='none', marker='o', color='black', fillstyle='none', label='Triple point')
    ax1.set_xlabel("Temperature ($^\circ$C)")
    ax1.set_ylabel("Presseure (Pa)")
    ax1.legend(loc='best')
    col2.pyplot(fig1)