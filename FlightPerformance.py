import math
import unittest
from apc_prop_reader import APCProp

apc12x6 = APCProp('PER3_12x6EP(F2B)')

class DesignPoint(object):
    def __init__(self):
        self.w = 2.6
        self.mass = 13.621
        self.S = 0.1009375*2.6**2
        self.AR = 8
        self.cd0 = 0.03
        self.profiledrag = 0.0078
        self.clmax = 1.3
        self.n = 1.3
        self.pe = 0.325
        self.Capacity = 34*60*60
        self.Voltage = 37
        self.Rt = 3600
        self.U = 20
        self.rho = 1.225
        self.prop = APCProp('PER3_20x13E')
        self._power = None
        self._endurance = None
        self._therance = None
        
    @property
    def k(self):
        return 1 / (math.pi * self.AR) + self.profiledrag

    @property
    def q(self):
        return 0.5 * self.rho * self.U**2

    @property
    def cl(self):
        return 9.81 * self.mass / (self.q * self.S)

    @property
    def cd(self):
        return (self.cd0 + self.k * self.cl ** 2)

    @property
    def preq(self):
        return self.q * self.U * self.cd * self.S / self.pe
    
    @property
    def drag(self):
        return self.q * self.S * self.cd
    
    @property
    def power(self):
        if not self._power:
            self._power = self.drag * self.U / (self.pe * self.prop.get_pe(self.U, 0.5*self.drag))
        return self._power
    
    @property
    def endurance(self):
        if self.is_stalled:
            return 0
        return ((self.Voltage * self.Capacity / self.power ) ** self.n ) * self.Rt ** (1 - self.n)
    
    @property
    def therange(self):
        return self.endurance * self.U
    
    @property
    def stall_speed(self):
        return math.sqrt(2*self.mass*9.81/(self.rho*self.S*self.clmax))
    
    @property
    def is_stalled(self):
        return self.U < self.stall_speed
    
    def to_dict(self):
        return {
            'mass':self.mass,
            'w': self.w,
            'S':self.S,
            'AR':self.AR,
            'cd0':self.cd0,
            'profiledrag':self.profiledrag,
            'clmax':self.clmax,
            'n':self.n,
            'pe':self.pe,
            'capacity':self.Capacity,
            'voltage':self.Voltage,
            'Rt':self.Rt,
            'U':self.U,
            'rho':self.rho,
            'prop':self.prop.name,
            'k': self.k,
            'q': self.q,
            'stall_speed': self.stall_speed,
            'is_stalled': self.is_stalled,
            'cl':self.cl,
            'cd':self.cd,
            'drag':self.drag,
            'power':self.power,
            'endurance': self.endurance,
            'range': self.therange
        }
    
    def copy(self):
        new_ac = DesignPoint()
        new_ac.w = self.w
        new_ac.mass = self.mass
        new_ac.S = self.S
        new_ac.AR = self.AR
        new_ac.cd0 = self.cd0
        new_ac.profiledrag = self.profiledrag
        new_ac.clmax = self.clmax
        new_ac.n = self.n
        new_ac.pe = self.pe
        new_ac.Capacity = self.Capacity
        new_ac.Voltage = self.Voltage
        new_ac.Rt = self.Rt
        new_ac.U = self.U
        new_ac.rho = self.rho
        new_ac.prop = self.prop
        new_ac._power = None
        return new_ac
    
buddita = DesignPoint()
buddita.mass = 3.2
buddita.S = 0.272
buddita.AR = 8
buddita.cd0 = 0.03
buddita.profiledrag = 0.0078
buddita.clmax = 1.3
buddita.Capacity = 10*60*60
buddita.Voltage = 24
buddita.Rt = 3600
buddita.U = 20
buddita.rho = 1.225
buddita.prop = APCProp('PER3_12x6EP(F2B)')


class TestDesignPoint(unittest.TestCase):
    def test_cl(self):
        self.assertAlmostEqual(DesignPoint().cl, 0.73872085)
    def test_preq(self):
        self.assertAlmostEqual(DesignPoint().preq, 187.1316955)
    def test_q(self):
        self.assertAlmostEqual(DesignPoint().q, 245)
    def test_k(self):
        self.assertAlmostEqual(DesignPoint().k, 0.047588736)
    def test_cd(self):
        self.assertAlmostEqual(DesignPoint().cd, 0.05596958)

if __name__ == "__main__":
    #unittest.main()
    for i in range(18, 33):
        buddita.U = i
        print(buddita.preq)