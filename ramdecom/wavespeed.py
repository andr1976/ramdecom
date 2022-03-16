import math
import numpy as np
from tqdm import tqdm
from matplotlib import pyplot as plt
from CoolProp.CoolProp import PropsSI
import CoolProp.CoolProp as CP

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
        pass

    def read_input(self):
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
        
    def initialize(self):
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
        rho1 = PropsSI('Dmass', 'S', Smass, 'P', P1, self.fluid_string)
        P2=P1+self.del_P
        rho2 = PropsSI('Dmass', 'S', Smass,'P',P2, self.fluid_string)
        return math.sqrt((P2-P1)/(rho2-rho1))

    def get_dataframe(self):
        pass

    def plot(self):
        if self.single_component:
            pc = self.asfluid.keyed_output(CP.iP_critical)
            Tc = self.asfluid.keyed_output(CP.iT_critical)
            Tt = self.asfluid.keyed_output(CP.iT_triple)
            pt = self.asfluid.keyed_output(CP.iP_triple)

            Ts = np.linspace(Tt, Tc, 100)
            ps = CP.PropsSI('P','T',Ts,'Q',0,self.fluid_string)

            plt.plot(Ts,ps)
            plt.plot(self.T,self.P)
            plt.show()
        else:
            self.asfluid.build_phase_envelope("")
            PE = self.asfluid.get_phase_envelope_data()
            plt.plot(PE.T,PE.p)
            plt.plot(self.T,self.P)
            plt.show()

    def run(self,disable_pbar=True):
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
    #CP.set_config_bool(CP.REFPROP_USE_GERG,True)
    #CP.set_config_bool(CP.REFPROP_USE_PENGROBINSON,True)
    input['temperature'] = 273.15+40
    input['pressure'] = 104.e5
    input['eos'] = 'REFPROP'
    input['fluid'] = 'CO2'
    ws = WaveSpeed(input)
    ws.run()

    data=np.loadtxt(r"\\ramoil.ramboll-group.global.network\Common\GlobalProjects\2015\1100019239\P-Process\CCS\CO2\CO2 decompression\Menkejord_test_6.txt",delimiter='\t')
    
    plt.plot(ws.W,ws.P,'k--',label="Calculated")
    plt.plot(data[:,0],data[:,1]*1e5,'ko',label="Experimental")
    plt.legend(loc='best')
    plt.xlabel("Decompression wave speed (m/s)")
    plt.ylabel("Pressure (Pa)")
    plt.show()