import math
import numpy as np
from matplotlib import pyplot as plt
from cerberus import Validator
from cerberus.errors import ValidationError 
from CoolProp.CoolProp import PropsSI
import CoolProp.CoolProp as CP


def validate_mandatory_ruleset(input):
    """
    Validate input file using cerberus

    Parameters
    ----------
    input : dict
        Structure holding input

    Return
    ----------
    retval : bool
        True for success, False for failure
    """

    schema_general = {
        'temperature': {
            'required': True,
            'type': 'number',
            },
        'pressure': {
            'required': True,
            'type': 'number',
        },
        'eos': {
            'required': True,
            'type': 'string',
            'allowed': ['HEOS', 'REFPROP']
        },
        'fluid': {
            'required': True,
            'type': 'string',
        },
        'refprop_option': {
            'required': False,
            'type': 'string',
            'allowed': ['GERG','PR']
        },
    }

    v = Validator(schema_general)
    retval = v.validate(input)
    if v.errors:
        print(v.errors)

    return retval


class InputError(Exception):
    """Base class for exceptions in this module."""
    pass


class WaveSpeed:
    """
    Main class to to hold problem definition, running problem, storing results, plotting etc.
    """

    def __init__(self, input):
        """
        Parameters
        ----------
        input : dict
            Dict holding problem definition
        """
        self.input = input
        self.del_P = 100 
        self.single_component = True
        self.validate_input()
        self.read_input()
        self.initialize()
        
    def validate_input(self):
        """
        Validating the dictionary provided as input with cerberus according to the defined schema
        """
        if validate_mandatory_ruleset(self.input) is False:
            raise InputError("Input file error")
        

    def read_input(self):
        """
        Reading in the provided input dict and storing in class 
        attributes. 
        """
        self.P_step = 1e5
        self.T0 = self.input['temperature']
        self.P0 = self.input['pressure']
        self.eos = self.input['eos']
        self.fluid = self.input['fluid']
        self.fluid_string = self.eos + '::' + self.input['fluid']
        self.max_step = int(self.P0 / self.P_step)
        
        if "&" in self.input["fluid"]:
            comp_frac_pair = [str.replace("["," ").replace("]","").split(" ") for str in  self.input["fluid"].split("&")] 
            comp = [pair[0] for pair in comp_frac_pair]
            molefracs = np.asarray([float(pair[1]) for pair in comp_frac_pair])
            molefracs = molefracs / sum(molefracs)
            self.molefracs = molefracs
            sep = "&"
            self.comp = sep.join(comp)
            self.single_component = False
        # Normally single component fluid is specified
        else:
            self.comp = self.input["fluid"]
            self.molefracs = [1.0]
        
        if self.eos == 'REFPROP' and 'refprop_option' in self.input:
            if self.input['refprop_option'] == 'GERG':
                CP.set_config_bool(CP.REFPROP_USE_GERG,True)
            elif self.input['refprop_option'] == 'PR':
                CP.set_config_bool(CP.REFPROP_USE_PENGROBINSON,True)
    

    def initialize(self):
        """
        Setting inital entropy for the isentrope, and preparing lists 
        for storing results. 
        """
        self.S0 = PropsSI('Smass', 'P', self.P0, 'T', self.T0, self.fluid_string)
        self.asfluid = CP.AbstractState(self.eos, self.comp)
        self.asfluid.set_mole_fractions(self.molefracs)
        self.asfluid.update(CP.PT_INPUTS, self.P0, self.T0)
        self.T = []
        self.P = []
        self.S_mass = []
        self.H_mass = []
        self.rho_mass = []
        self.Q = []
        self.C = []
        self.U = []
        self.W = []        


    def speed_of_sound(self, Smass, P1):
        """
        Generic calculation of the fluid speed of sound using 
        a finite difference approximation to the expression
        at constant entropy: 

        C = (d_P/d_rho)^0.5 
          = ((P1-P2)/(rho1-rho2))^0.5

        A default difference between P1 and P2 of 100 Pa is used.
        Rho is evalated isentropically at the corresponding pressure
        and provided entropy. 

        Parameters
        ----------
        Smass: float
            Mass specific entropy of the fluid 
        P1: float
            The pressure at the isentrope at which the speed of sound 
            shall be calculated
            
        Return
        ----------
        retval : float 
            Speed of sound    
        """
        
        rho1 = PropsSI('Dmass', 'S', Smass, 'P', P1, self.fluid_string)
        P2=P1+self.del_P
        rho2 = PropsSI('Dmass', 'S', Smass,'P',P2, self.fluid_string)
        return math.sqrt((P2-P1)/(rho2-rho1))

    def get_dataframe(self):
        pass

    def plot_envelope(self,t_min=250):
        """
        Convenience function to provide easy plotting of the 
        isentropic path in the phase diagram / PT-envelope. 
        Checking is made if fluid is single component, then the saturation 
        curve from triple to critical point is calculated, else for mixture 
        the phase envelope is calculated. 
        """

        if self.single_component:
            pc = self.asfluid.keyed_output(CP.iP_critical)
            Tc = self.asfluid.keyed_output(CP.iT_critical)
            Tt = self.asfluid.keyed_output(CP.iT_triple)
            pt = self.asfluid.keyed_output(CP.iP_triple)

            Ts = np.linspace(Tt, Tc, 100)
            ps = CP.PropsSI('P','T',Ts,'Q',0,self.fluid_string)

            plt.plot(Ts,ps,color='dimgrey', label='Saturation line')
            plt.plot(self.T,self.P,'k--', label='Isentropic path')
            plt.plot(Tc,pc,'ko', label='Critical point')
            plt.plot(Tt,pt, linestyle='none', marker='o', color = 'black', fillstyle='none', label='Triple point')
            plt.plot(self.T0,self.P0, linestyle='none', marker='o', color='k',  fillstyle='right', label='Initial state')
        else:
            self.asfluid.build_phase_envelope("")
            PE = self.asfluid.get_phase_envelope_data()
            plt.plot(PE.T,PE.p,'k--',label='Phase envelope')
            plt.plot(self.T,self.P,'k',label='Isentropic path')
            t_max = max(self.T0, 310) + 10.
            plt.xlim(t_min,t_max)

        plt.xlabel('Temperature (K)')
        plt.ylabel('Pressure (Pa)')
        plt.legend(loc='best')
        plt.show()

    def plot_decom(self):
        """
        Convenience function to provide easy plotting of the 
        pressure vs decompression wave speed. 
        """
        plt.plot(self.W,self.P,'k--',label="Calculated")
        plt.legend(loc='best')
        plt.xlabel("Decompression wave speed (m/s)")
        plt.ylabel("Pressure (Pa)")
        plt.show()

    def run(self,disable_pbar=False):
        """
        Main function to run through the isentropic path from initial P,T
        and stepping down in P along the isentrope. For each pressure step
        the speed of sound, the maximum velocity and resulting decompression 
        speed, W, is calculated until teh stopping criterium is met, which is either 
        P < 1e5 Pa or W < 0.
        """
        for i in range(self.max_step):
            if i == 0:
                Tguess = self.T0
            else:
                Tguess = self.T[-1]

            P_new = self.P0-self.P_step*i
            T_new = PropsSI('T','P',P_new,'S',self.S0,self.fluid_string)
            #S_mass = PropsSI('Smass', 'P', P_new, 'T', T_new, self.fluid_string)
            H_mass = PropsSI('Hmass', 'P', P_new, 'S', self.S0, self.fluid_string)
            Q = PropsSI('Q', 'P', P_new, 'S', self.S0, self.fluid_string)
            
            if Q < 0: 
                Q = 0 
            elif Q > 1: 
                Q = 1

            D_mass = PropsSI('Dmass', 'P', P_new, 'S', self.S0, self.fluid_string)
            
            C = self.speed_of_sound(self.S0, P_new)

            if i == 0:
                U = (self.P0 - P_new) / (C * D_mass)
            else:
                U = self.U[i-1] + (self.P[i-1] - P_new) / (C * D_mass)

            W = C - U

            if P_new < 1e5 or W < 0: 
                print("Stopping at P (Pa):", P_new, "and wavespeed (m/s):", W)
                break

            self.C.append(C)
            self.P.append(P_new)    
            self.T.append(T_new)
            self.Q.append(Q)
            self.H_mass.append(H_mass)
            self.U.append(U)
            self.W.append(W)
            self.rho_mass.append(D_mass)

if __name__ == '__main__':
    input = {}
    input['temperature'] = 273.15+35.09
    input['pressure'] = 145.61e5
    input['eos'] = 'REFPROP'
    input['fluid'] = 'CO2[0.9667]&O2[0.0333]'
    #input['refprop_option']='GERG'
    ws = WaveSpeed(input)
    ws.run()

    data=np.loadtxt(r"..\validation\Botros_Test_4.txt",delimiter='\t')
    
    plt.plot(ws.W,ws.P,'k--',label="Calculated")
    plt.plot(data[:,0],data[:,1]*1e5,'ko',label="Experimental")
    plt.legend(loc='best')
    plt.xlabel("Decompression wave speed (m/s)")
    plt.ylabel("Pressure (Pa)")
    plt.show()