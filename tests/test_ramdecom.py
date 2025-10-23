# RAMDECOM Copyright (c) 2022 Anders Andreasen

from ramdecom import wavespeed
import pytest
import os

def test_pure_run_coolprop():
    input = {}
    input['temperature'] = 273.15+35.09
    input['pressure'] = 145.61e5
    input['eos'] = 'HEOS'
    input['fluid'] = 'CO2'
    ws = wavespeed.WaveSpeed(input)
    ws.run()
    assert ws.T[-1] == pytest.approx(278.0666028440005, rel=1e-5)
    assert ws.P[-1] == pytest.approx(3961000.0, rel=1e-5)
    assert ws.rho_mass[-1] == pytest.approx(362.33658068836274, rel=1e-5)

def test_pure_run_coolprop_extended():
    input = {}
    input['temperature'] = 273.15+35.09
    input['pressure'] = 145.61e5
    input['eos'] = 'HEOS'
    input['fluid'] = 'CO2'
    input['extrapolate'] = True
    input['pressure_break'] = 45e5
    ws = wavespeed.WaveSpeed(input)
    ws.run()
    assert ws.T[-1] == pytest.approx(283.67432227384006, rel=1e-5)
    assert ws.P[-1] ==  pytest.approx(4561000.0, rel=1e-5)
    assert ws.rho_mass[-1] == pytest.approx(454.99417292135354, rel=1e-5)


def test_pure_run_refprop():
    input = {}
    input['temperature'] = 273.15+35.09
    input['pressure'] = 145.61e5
    input['eos'] = 'REFPROP'
    input['fluid'] = 'CO2'
    try:
        ws = wavespeed.WaveSpeed(input)
        ws.run()
        ws.plot_decom(filename=os.devnull)
        ws.plot_envelope(filename=os.devnull)
        assert ws.T[-1] == 278.0666028427595
        assert ws.P[-1] == 3961000.0
        assert ws.rho_mass[-1] == 362.33658073279605
    except:
        pass

def test_mixture_run():
    input = {}
    input['temperature'] = 273.15+35.09
    input['pressure'] = 145.61e5
    input['eos'] = 'REFPROP'
    input['fluid'] = 'CO2[0.9667]&O2[0.0333]'
    try:
        ws = wavespeed.WaveSpeed(input)
        ws.run()
        ws.plot_decom(filename=os.devnull)
        ws.plot_envelope(filename=os.devnull)
        assert ws.T[-1] == 276.5007018160266
        assert ws.P[-1] == 4361000.0
        assert ws.rho_mass[-1] == 329.8561371724617
    except: 
        pass

def test_mixture_run_PR():
    input = {}
    input['temperature'] = 273.15+35.09
    input['pressure'] = 145.61e5
    input['eos'] = 'REFPROP'
    input['fluid'] = 'CO2[0.9667]&O2[0.0333]'
    input['refprop_option'] = 'PR'
    input['pressure_step'] = 2e5
    input['extrapolate'] = True
    try:
        ws = wavespeed.WaveSpeed(input)
        ws.run()
        ws.plot_decom(filename=os.devnull)
        ws.plot_envelope(filename=os.devnull)
        assert ws.T[-1] == 275.3431334865607
        assert ws.P[-1] ==  4161000.0
        assert ws.rho_mass[-1] == 323.03722458518354
    except: 
        pass

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
    
