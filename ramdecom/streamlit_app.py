# RAMDECOM
# Copyright (c) 2022 Anders Andreasen
# Published under an MIT license

import streamlit as st
import pandas as pd
from PIL import Image
import base64

try:
    from ramdecom import wavespeed
except:
    import sys
    import os
    hyddown_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "..", "ramdecom")
    sys.path.append(os.path.abspath(hyddown_path))
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

        # with st.form(key='my_form'):
        #     submit_button = st.form_submit_button(label='Run calculation')
        #     temp = float(st.text_input('Initial temp. (C):', 25))
        #     pres = float(st.text_input('Initial pressure (bar):', 50.))
        
    input = {}
    input['temperature'] = 273.15 + temp
    input['pressure'] = pres * 1e5
    input['eos'] = 'HEOS'
    input['fluid'] = 'CO2'
    return input 

if __name__ == "__main__":
    st.set_page_config(layout='wide')

    ws = WaveSpeed(input)
    ws.run()

    with st.spinner('Calculating, please wait....'):
        hdown.run(disable_pbar=True) 

    st.title('Pure CO2 pipeline decompression wavespeed')
    st.subheader(r'https://github.com/andr1976/RAMDECOM')
    my_expander = st.expander("Description")

    my_expander.write('Calculation of decompression wavespeed using the CoolProp library. Results to be used in combination with e.g. the Battelle two-curve method.')

    df = ws.get_dataframe()
    file_name = st.text_input('Filename for saving data:', 'saved_data') 
    
    st.markdown(get_table_download_link(df, file_name), unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    # if input['valve']['flow'] == 'discharge':
    #     temp_data = pd.DataFrame({'Time (s)': hdown.time_array, 'Fluid temperature (C)': hdown.T_fluid-273.15, 'Wall temperature (C)': hdown.T_vessel-273.15, 'Vent temperature (C)': hdown.T_vent-273.15})
    # else:
    #     temp_data = pd.DataFrame({'Time (s)': hdown.time_array, 'Fluid temperature (C)': hdown.T_fluid-273.15, 'Wall temperature (C)': hdown.T_vessel-273.15})

    # pres_data = pd.DataFrame({'Time (s)': hdown.time_array, 'Pressure (bar)': hdown.P/1e5})

    # col1.line_chart(pres_data.rename(columns={'Time (s)': 'index'}).set_index('index'))
    # col1.text('Time (s)')
    # col2.line_chart(temp_data.rename(columns={'Time (s)': 'index'}).set_index('index'))
    # col2.text('Time (s)')    

    # mdot_data = pd.DataFrame({'Time (s)': hdown.time_array, 'Mass rate (kg/s)': hdown.mass_rate})
    # mass_data = pd.DataFrame({'Time (s)': hdown.time_array, 'Fluid inventory (kg)': hdown.mass_fluid})
    # col1.line_chart(mdot_data.rename(columns={'Time (s)': 'index'}).set_index('index'))
    # col1.text('Time (s)')
    # col2.line_chart(mass_data.rename(columns={'Time (s)': 'index'}).set_index('index'))
    # col2.text('Time (s)')
