import math
import numpy as np
from tqdm import tqdm
from scipy.optimize import minimize
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
        self.fluid_string = eos + '::' + self.input['fluid']
        self.max_step = self.P0/self.P_step
        
        if "&" in self.input["fluid"]:
            comp_frac_pair = [str.replace("["," ").replace("]","").split(" ") for str in  self.input["initial"].split("&")] 
            comp = [pair[0] for pair in comp_frac_pair]
            molefracs = np.asarray([float(pair[1]) for pair in comp_frac_pair])
            molefracs = molefracs / sum(molefracs)
            self.molefracs = molefracs
            sep = "&"
            self.comp = sep.join(comp)
        # Normally single component fluid is specified
        else:
            self.comp = self.input["fluid"]
            self.molefracs = [1.0]
        
    def initialize(self):
        self.fluid = CP.AbstractState(self.eos, self.comp)
        self.fluid.set_mole_fractions(self.molefracs)
        self.fluid.update(CP.PT_INPUTS, self.P0,  self.T0)
        self.S0 = self.fluid.smass()

        self.T = []
        self.P = []
        self.S_mass = []
        self.H_mass = []
        self.rho_mass = []
        

    def PSres(self, T, P, S):
        """
        Residual enthalpy function to be minimised during a PH-problem
        
        Parameters
        ----------
        S : float 
            Entropy at initial/final conditions
        P : float
            Pressure at final conditions. 
        T : float 
            Updated estimate for the final temperature at P,H
        """
        self.fluid.update(CP.PT_INPUTS, P, T)
        return ((S-self.fluid.smass())/S)**2 

    def PSproblem(self, P, S, Tguess):
        """
        Defining a constant pressure, constant entropy problem i.e. typical isentropic 
        problem like e.g. decompression/compression. 
        For multicomponent mixture and/or cubic EOS the final temperature is changed/optimised 
        until the residual enthalpy is near zero in an optimisation step. For single component 
        fluid the coolprop built in methods are used for speed. 
        
        Parameters
        ----------
        P : float
            Pressure at final conditions. 
        S : float 
            Entropy at initial/final conditions
        Tguess : float 
            Initial guess for the final temperature at P,S
        """

        # Multicomponent case
        if "&" in self.species:                     
            x0 = Tguess
            res = minimize(self.PSres, x0, args=(P, S), method='Nelder-Mead', options={'xatol':0.1,'fatol':0.001})
            T1 = res.x[0]
        # single component fluid case
        else:
            T1 = PropsSI(
                "T", "P", P, "S", S, self.species
               )  
        return T1

    def get_dataframe(self):
        pass

    def plot(self):
        pass

    def run(self,disable_pbar=True):
        pass