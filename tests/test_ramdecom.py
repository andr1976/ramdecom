from ramdecom import wavespeed

def test_pure_run_coolprop():
    input = {}
    input['temperature'] = 273.15+35.09
    input['pressure'] = 145.61e5
    input['eos'] = 'HEOS'
    input['fluid'] = 'CO2'
    ws = wavespeed.WaveSpeed(input)
    ws.run()
    assert ws.T[-1] == 278.0666028440005
    assert ws.P[-1] == 3961000.0
    assert ws.rho_mass[-1] == 362.33658068836274

def test_pure_run_refprop():
    input = {}
    input['temperature'] = 273.15+35.09
    input['pressure'] = 145.61e5
    input['eos'] = 'REFPROP'
    input['fluid'] = 'CO2'
    ws = wavespeed.WaveSpeed(input)
    ws.run()
    assert ws.T[-1] == 278.0666028427595
    assert ws.P[-1] == 3961000.0
    assert ws.rho_mass[-1] == 362.33658073279605

def test_mixture_run():
    input = {}
    input['temperature'] = 273.15+35.09
    input['pressure'] = 145.61e5
    input['eos'] = 'REFPROP'
    input['fluid'] = 'CO2[0.9667]&O2[0.0333]'
    ws = wavespeed.WaveSpeed(input)
    ws.run()
    assert ws.T[-1] == 276.5007018160266
    assert ws.P[-1] == 4361000.0
    assert ws.rho_mass[-1] == 329.8561371724617

def test_input_validation():
    input = {}
    input['temperature'] = 'a'
    input['pressure'] = 145.61e5
    input['eos'] = 'REFPROP'
    input['fluid'] = 'CO2[0.9667]&O2[0.0333]'
    try:
        ws = wavespeed.WaveSpeed(input)
    except wavespeed.InputError as err:
        assert str(err) == 'Input file error'
    
    input['temperature'] = 300
    input['eos'] = 'SRK'
    try:
        ws = wavespeed.WaveSpeed(input)
    except wavespeed.InputError as err:
        assert str(err) == 'Input file error'
    
    input['eos'] = 'REFPROP'
    input['fluid'] = 120
    try:
        ws = wavespeed.WaveSpeed(input)
    except wavespeed.InputError as err:
        assert str(err) == 'Input file error'
    
    input['fluid'] = 'CO2'
    input['pressure'] = 'a'
    try:
        ws = wavespeed.WaveSpeed(input)
    except wavespeed.InputError as err:
        assert str(err) == 'Input file error'
    