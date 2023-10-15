from time import sleep
import RPi.GPIO as GPIO


class stepper_motor: # stepper motor control

             
    def __init__(self, DIR, STEP, MODE, CW, mstep, EN):# how do I take an input arguemt to the init function
                                                        # that is a key for the RES dictionary, so I can define microsteps
                                                        # resolution, solution not elegant
        
        self.DIR = DIR
        self.STEP = STEP
        self.MODE = MODE
        self.CW = CW
        self.mstep = mstep # expect string number e.g. '1'
        self.EN = EN
        
        self.steps_per_rev = 200*(int(mstep)) # where mstep is the microstepping factor
        self.delay = 1/(200*int(mstep))
                          # 1 / 200 for '1', since int(mstep) = 1, keeping 1 rev == 1 second
        
        RES = {'1': (0,0,0), # resolution (M2,M1,M0)
                    '2': (0,0,1),
                    '4': (0,1,0),
                    '8': (0,1,1),
                    '16': (1,0,0),
                    '32': (1,0,1)
                     }
        
        self.position = 0 # set the ballscrew to 0 mm travel
        
        # Configure the GPIOs
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM) # Uses GPIO numbers rather than pin numbers
        GPIO.setup(self.DIR, GPIO.OUT) # sets direction pin as output
        GPIO.setup(self.STEP, GPIO.OUT) # sets step pin as output
        GPIO.setup(self.MODE, GPIO.OUT) # sets the mode pins - 14,15,18 to output
        GPIO.setup(self.EN, GPIO.OUT)
        
        x = RES.get(mstep)
        
        GPIO.output(self.DIR, self.CW) # set DIR to clockwise
        GPIO.output(MODE, x) # sets the microstep resolution
        GPIO.output(EN, 0) # make Enable initially low
    
    def set_direction(self, direction):
        if direction == 'CW':
            self.CW = 1 # This is the direction valariable
            GPIO.output(self.DIR, self.CW)        
        elif direction == 'CCW':
            self.CW = 0
            GPIO.output(self.DIR, self.CW)
        else:
            print('Invalid direction argument')
            
    def move(self,displacement):
        # displacement ALWAYS in mm
        # 1 rev = 4 mm lead of the ballscrew
        leadconv = displacement/4
        step_count = leadconv*(self.steps_per_rev)
        # steps per rev is the constant determined earlier of 200*mstep value
        
        print('d = ' + str(displacement) + ' mm' + ' which is ' + str(step_count) + ' steps.')
        
        GPIO.output(self.EN,1) # enable the driver and motor
        for i in range(int(step_count)):
            GPIO.output(self.STEP, GPIO.HIGH)
            sleep(self.delay)
            GPIO.output(self.STEP, GPIO.LOW)
            sleep(self.delay)
        GPIO.output(self.EN,0) # disable the driver and motor
        #print('loop end')

    def moveto(self,stroke): # enter position stroke length in mm to move to
                        # if you enter your current location, motor will not move
        dis = stroke - self.position
        
        if stroke < 0:
            print('error, already at 0')
        elif dis<0:
            self.set_direction('CCW')
            self.position = self.position + dis
        else:
            self.set_direction('CW')
            self.position  = self.position + dis
            
        self.move(abs(dis))
        print('current position = ' + str(self.position) + ' mm')
            
            #need a position system, store the current position in a saved variable?
            #in case of power down
            #can manually record the steps / displacement when doing the calibration test

#test = stepper_motor(20, 21, (26,19,13), 1, '8', 16)

#test.moveto(4)