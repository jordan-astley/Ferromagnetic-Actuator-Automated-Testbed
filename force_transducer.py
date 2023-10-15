from hx711 import HX711

class load_cell:
    
    def __init__(self, DT=5, SCK=6):
        
        self.DT = DT
        self.SCK = SCK
        
        self.hx = HX711(DT,SCK) # HX711(DT,SCK)
                        # parameter 1:data out pin (DT), parameter 2: SCK (serial clk pin)
                        # tells the Pi what pins the hx711 is connected on, e.g 5 = GPIO 5
        
        self.hx.reset()#powers down and then powers up the hx711

        self.hx.set_reading_format("MSB")
    
    def raw_val(self):
        reading = self.hx.read_long()
        return reading
        
    def print_raw(self):
        while True:
            reading = self.hx.read_long()
            print(reading)

    def print_av_reading(self):
        while True:
            reading = self.hx.read_average(10)
            print(str(reading))
            
    def average_read(self):
        reading = self.hx.read_average(25)
        #print(str(reading))
        return reading

    def get_force(self, r): # r is number of samples to get mean from
        raw_reading = self.hx.read_average(r)
        # y = mx +c
        m = 0.0001271
        c = (-10.25)
        # x = raw_reading
        force = (m*float(raw_reading)) + c
        #if force<0:
            #return(0)
        #else:
        return(force) # returns the force value calculated from the linear approximation of the load cell.