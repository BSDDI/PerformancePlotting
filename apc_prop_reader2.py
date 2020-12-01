import numpy as np
import pandas as pd
from io import open
import re
import requests
from urllib.error import HTTPError
from pint import UnitRegistry
import tempfile
from scipy.interpolate import interp2d
import unittest
ureg = UnitRegistry()


class APCProp(object):

    desired_units = {
        'rpm': 1/ureg.minute,
        'V': ureg.meter / ureg.second, 
        'J': ureg.dimensionless, 
        'Pe': ureg.dimensionless, 
        'Ct': ureg.dimensionless, 
        'Cp': ureg.dimensionless, 
        'PWR': ureg.watt, 
        'Torque': ureg.N * ureg.meter, 
        'Thrust': ureg.N
    }


    def __init__(self, dat_file_name):
        self.dat_file = self._get_dat_file(dat_file_name)
        self.diameter = re.search('\d+x', dat_file_name).group(0)
        self.pitch = re.search('x\d+', dat_file_name).group(0)
        self.performance = APCProp.read_prop_dat(self.dat_file)
        self.units = {key: ureg.dimensionless for key in self.performance.columns }
        self.units['rpm'] = 1/ureg.minute
        self.units['V'] = ureg.mph
        self.units['PWR'] = ureg.hp
        self.units['Torque'] = ureg.inch * ureg.lbf
        self.units['Thrust'] = ureg.lbf
        self._unit_convert()
        self.get_pwr = interp2d(self.performance.V.values, self.performance.Thrust.values, self.performance.PWR.values)

        
    def _get_dat_file(self, file):
        target_file = tempfile.gettempdir() + '/' + file
        url = "https://www.apcprop.com/files/" + file
        r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        with open(target_file, 'wb') as outfile:
            outfile.write(r.content)
        return target_file
        
    @staticmethod
    def read_prop_dat(file):
        rpm=0
        data = []
        with open(file, 'r') as inf:
            for line in inf.readlines():
                nums = re.search('\d+',line)
                if 'PROP RPM =' in line:
                    rpm = int(nums.group(0))
                    continue
                if rpm > 0 and not line.isspace():
                    if not nums:
                        continue
                    vals = [rpm]
                    for val in line.split():
                        try:
                            vals.append(float(
                                re.search('[-+]?([0-9]*\.[0-9]+|[0-9]+)',val).group(0)
                            ))
                        except:
                            continue
                    if len(vals) < 8:
                        continue
                    data.append(vals)
        
        df=pd.DataFrame(data, columns=['rpm', 'V', 'J', 'Pe', 'Ct', 'Cp', 'PWR', 'Torque', 'Thrust'])

        return df

    #def get_pwr(self, V_val, Thrust_val):
    #    pwr_val = interp2d(self.performance.V.values, self.performance.Thrust.values, self.performance.PWR.values, np.array([V_val, Thrust_val]).T)
    #    return pwr_val
        
    @staticmethod
    def conv(value, fromunit, tounit):
        return ureg.Quantity(value, fromunit).to(tounit).magnitude

    def _unit_convert(self):
        for col in self.performance.columns.to_list():
            self.performance[col]=self.performance[col].apply(APCProp.conv, args=(self.units[col], APCProp.desired_units[col]))

        


class TestSimulation(unittest.TestCase):
    def setUp(self):
        self.prop = APCProp('PER3_12x6.dat')
        pass
    '''def test_perf(self):
        perf = self.prop.performance
        temp=perf.loc[perf['rpm']==18000]
        temp2 = temp.loc[temp['V']==55.522368]
        self.assertEqual(temp2['Pe'].values[0], .6741)'''
    
    def test_pwr_1(self):
        self.assertAlmostEqual(self.prop.get_pwr(0.268224000000000, 0.306927291452975)[0], 0.745699871582270, places=1)
    def test_pwr_11(self):
        self.assertAlmostEqual(self.prop.get_pwr(1.78816000000000, 0.213514637532504)[0], 0.745699871582270, places=1)
    def test_pwr_2(self):
        self.assertAlmostEqual(self.prop.get_pwr(2.05638400000000, 1.08981429573882)[0], 5.21989910107589, places=1)  
    def test_pwr_21(self):
        self.assertAlmostEqual(self.prop.get_pwr(3.84454400000000, 0.809576333977411)[0], 5.21989910107589, places=1)
    def test_pwr_3(self):
        self.assertAlmostEqual(self.prop.get_pwr(8.89609600000000, 0.849610328514756)[0], 10.4397982021518, places=1)  

    def test_pwr_8(self):
        self.assertAlmostEqual(self.prop.get_pwr(34.6903040000000, 89.8451801850316)[0], 5621.08563198715, places=1)      
if __name__ == "__main__":
    unittest.main()