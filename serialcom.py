import serial

class power_supply:
    
    def __init__(self):
        
        self.ser = serial.Serial(
            port='/dev/ttyACM0', # establish connection on correct port
            baudrate=9600,       # configuring the connection
            bytesize=8,
            parity='N',
            stopbits=1,
            xonxoff = 0,
            dsrdtr = 0,
            write_timeout = 0)
        
    # method definitions to send commands to supply over usb    
                
    def set_voltage(self,v):
        if abs(v) > 30:
            print('voltage exceeds max')
        else:
            arg = "VSET1:" + str(abs(v))
            arg_return = arg + str('\\n')# \\ (ESC the ESC)
            #print(arg)
            #print(arg_return)
            self.ser.write(arg_return.encode(encoding="ascii"))# encode in bytes array, ser.write will not accept strings/concatenations
            print('Voltage: ' + str(abs(v)) + ' V')
            
    def set_current(self,i):
        if abs(i) > 3:
            print('current exceeds max')
        else:
            arg = "ISET1:" + str(abs(i)) # take argument i and create string
            arg_return = arg + str('\\r\\n')# \\ (ESC the ESC), adding the new line etc
            #print(arg)
            #print(arg_return)
            self.ser.write(arg_return.encode(encoding="ascii")) # encode in bytes array with .encode()
            print('Current: ' + str(abs(i)) + ' A')

    def current_out(self): # returns the actual output current, for plotting accurately
            # no inputs dont care
        req = 'IOUT1?\\r\\n'
        self.ser.write(req.encode(encoding="ascii")) # request current out, byte array encoded
        x = self.ser.read(size=5) # create var looking for 5 bytes (4 digit number plus decimal point)

        # Problems encoutered here since pySerial will look to read the number of bytes
        # given. If there is no timeout, and to many bytes are given (i.e before I had
        # 10 bytes, size=10), it blocks and you get nothing printed in the terminal.
        #print(x) # print to check raw output
        x_return = x.decode("ascii") # decode from byte array
        #print(x_return) # print the 4 digit current value
        return x_return

    def voltage_out(self): # returns the actual output current, not the max
        req = 'VOUT1?\\r\\n' # no input parameters
        self.ser.write(req.encode(encoding="ascii")) # request voltage out, byte array encoded
        x = self.ser.read(size=5) # create var looking for 5 bytes (4 digit number + decimal point)

        print(x) # print to check raw output
        x_return = x.decode("ascii") # decode to remove the encoding
        print(x_return) # print the 4 digit voltage value
        return x_return
    
    def output(self,x): # turns the power supply output off and on
        if x == 'True':
            arg = "OUT1" + str('\\r\\n')# \\ (ESC the ESC)
            self.ser.write(arg.encode(encoding="ascii"))
            #print(arg)
            #print('power on')
        elif x == 'False':
            arg = 'OUT0' + str('\\r\\n')
            self.ser.write(arg.encode(encoding="ascii"))
            #print(arg)
            #print('power off')
            
        else:
            print('enter string true or false')

    # all this \r\n nonsense is due to python 3 storing data in unicode,
    # the write function needs data in bytes or bytearray
    # so you put the data into a byte array
    # the suffix simply means caridge return, new line
    # ser.write(b'VSET1:1\\r\\n')
    # ser.write(b'*IDN?\r\n') are original commands
#Example of use:        
#test = power_supply()
#test.set_voltage(10)
