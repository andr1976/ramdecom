[![DOI](https://zenodo.org/badge/505804194.svg)](https://zenodo.org/badge/latestdoi/505804194)
[![Python application](https://github.com/andr1976/ramdecom/actions/workflows/python_app.yml/badge.svg)](https://github.com/andr1976/ramdecom/actions/workflows/python_app.yml)
![license](https://img.shields.io/github/license/andr1976/ramdecom)
 [![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io/andr1976/ramdecom/main/scripts/streamlit_app.py)
 [![codecov](https://codecov.io/gh/andr1976/ramdecom/branch/main/graph/badge.svg)](https://codecov.io/gh/andr1976/ramdecom)


# RAMDECOM
Calculation routine to calculate the decompression wave speed for pipeline design to ensure adequate pipe thickness and/or Charpy-V hardness so a running fracture can be arrested. The program is mainly targeted for CO<sub>2</sub>, but almost any fluid can be modelled. 

This code is developed by Anders Andreasen and is open source and published under an [MIT license](https://gitlab.rambollgrp.com/anra/ramdecom/-/blob/main/LICENSE) . For pure fluids, calculations can be made using open source tools only ([CoolProp](www.coolprop.org)). However, if calculations shall be made for mixtures a [REFPROP](https://www.nist.gov/srd/refprop) license and installation is required.  

## Background and reference
The methods implemented in RAMDECOM are described in more detail in an *open access* publication in [Simulation Notes Europe](https://www.sne-journal.org/fileadmin/user_upload_sne/SNE_Issues_OA/SNE_32_4/articles/sne.32.4.10622.tn.OA.pdf). If you use RAMDECOM, please cite this article. 
A [color copy](paper/ramdecom_paper.pdf) is also included in this repository.

```
@article{ramdecom,
  author  = {{Andreasen, A. and Sousa, L-H and Agustsson, G.}},
  title   = {An Open Source Tool for Calculating CO2 Pipeline Decompression Wave Speed},
  doi     = {10.11128/sne.32.tn.10622},
  journal = {Simulation Notes Europe SNE},
  year    = 2022,
  volume  = 32,
  issue = 4,
  pages   = {187--193}
}
```

## Installation
The code is still under heavy development and official releases and pip/conda packages have not been prepared yet. Installation is done by cloning the code to a local directory and running 

```
cd directory
pip install -e .
```

This way a dynamic link is created in the local site-packages directory. Any changes to the code will be dynamically updated, so no need to run ``` pip install -e ``` every time the code is updated. 


## Usage

### Import main class
```
from ramdecom import wavespeed
```

### Define input
```
input = {}
input['eos'] = 'HEOS' 
input['fluid'] = 'CO2'
input['pressure'] = 130e5 
input['temperature'] = 320
``` 

The equation of state can either be ```HEOS``` for the CoolProp pure component Helmholtz energy formulation or [REFPROP](https://www.nist.gov/srd/refprop). For mixtures only ```REFPROP``` works. In case ```REFPROP``` is selected additional optional input for specifying either the [GERG-2008](https://www.thermo.ruhr-uni-bochum.de/thermo/forschung/wagner_GERG.html.de) or the Peng-Robinson equation of state can be given. The follwoing optional input can also be provided:

```
input['extrapolate'] = True
``` 

which will extrapolate the end point in the decompression curve to zero pressure. 

```
input['pressure_step'] = 1e5
```

defines the step length when stepping down from the initial pressure along the isentropic path. The default value is 1 bar and has been found to be adequate. 

```
input['pressure_break'] = 1e5
```

can break the isentropic decompression calculation e.g. if the calculation routine in the thermodyanmic backend raises an exception. By breaking before the exception is raised, partial results can be inspected and visualised. 

### Ininitialize and run
```
ws = wavespeed.WaveSpeed(input)    
ws.run()
```

### Plotting

```
ws.plot_decom(filename='out.png',data=data)
```

If the optional input  ```data``` (experimental data or other calculation for comparison) is provided this shall be a nx2 array with decompression wave speed in the first column and pressure in the second column. If the optional input ```filename``` is not provided the plot is displayed on-screen without being saved to file. 

### Other data output 
A data file with calculation results can be saved to csv

```
ws.get_result_file()
```
The results are saved to ```decom_result.csv``` or if the optional input  ```filename``` is given, it is saved to the provided path. 

## Methods and theory
Some basic theory and description of the code is included with the draft paper located in 

```
ramdecom\paper\
```

Further some relevant references for further reading: 

[1] http://pubs.acs.org/doi/abs/10.1021/ie4033999

[2] https://pubs.acs.org/doi/10.1021/acsomega.1c01360

[3] https://doi.org/10.18434/T4/1502528

[4] https://doi.org/10.1016/j.psep.2018.08.034

[5] https://doi.org/10.1115/1.4031941 

[6] https://doi.org/10.1115/1.4034016 
