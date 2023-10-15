#loop utility functions

import time

import csv
import matplotlib.pyplot as plt

import force_transducer
import serialcom
import stepper_motor_class

class loop_util:
    
    def __init__(self):
         
        #comment this section out for testing GUI
        self.power = serialcom.power_supply()
        self.reading = force_transducer.load_cell()
        self.motor = stepper_motor_classv2.stepper_motor(20, 21, (26,19,13), 1, '8', 16)
        #(self, DIR, STEP, MODE, CW, mstep, EN)
         
         
    ###################### operation methods ######################

    def set_power(self,i,v): #setting for 11W power in 14.4 ohm coil
        self.power.set_voltage(v) # cal = 14V
        time.sleep(.1)
        self.power.set_current(i) # cal = 0.874A
    
    def measure0(self): #measure the reading with no force applied
        self.power.output('False')
        time.sleep(1)
        x = self.reading.average_read()
        #print(x)
        return str(x)
    
    def measure(self): #measure and return the average function output from hx711 library reading
        self.power.output('True')
        time.sleep(1) #can change this is hx711 reading has not settled properly
        x = self.reading.average_read()
        self.power.output('False')
        return str(x)
    
############################ calibration data capture method ######################

#need to add way to define the file name of the plot and data

    def data_aquire_cal(self,times): #runs the test bed, times is an integer number defines how many loops of aquiring data
        
        time.sleep(1)
        
        self.set_power(0.874,14) # (i,v) sets 11W, 14.4 ohm coils
        
        ##force for each of predefined stroke lengths, read from the data sheet##
        force_vals = ['0','4.9','4.165','3.675','3.185','2.695','2.45','2.205','1.96','1.862','1.764','1.715']
        
        with open('./data/cal_loop_results.csv', 'w', newline='') as csv_file: #create csv file called loop_results
            
            csv_writer = csv.writer(csv_file, delimiter=',') # create writing object
            
            for t in range(times): # so data_aquire(5) to repeat the test 5 times
                
                count = 0 # counter for using the specific force_vals list entries, above
                # having the counter inside the for loop resets it each time, so the force vals are read correctly
                
                # measure 0 mm force output @ 0.874A, this will be our 0N point for calibrating the hx711
                # measures 0 force applied to load cell
                self.motor.moveto(0) 
                time.sleep(1)
                output = self.measure()
                csv_writer.writerow([str(0),str(force_vals[count]),str(output)])
                count = count + 1
                time.sleep(1)
                
                ##measure from 8mm to 18mm, in 1mm steps##
                for stroke in range(8,19,1): #(start,stop,step)
                    self.motor.moveto(stroke)
                    time.sleep(1)
                    output = self.measure()
                    csv_writer.writerow([str(stroke),str(force_vals[count]), str(output)])
                    count = count + 1
                    time.sleep(1)
                
                #status('loop ' + str(t) + ' done')
                self.motor.moveto(0) # reset back to 0
                
                # added write row force_vals, writes the incremented value of force from the force_vals list
                # this means when looking at the .csv file you have comma separated vars of:
                # stroke length, force(N), hx711 average output
                # it should use the correct force values, of which there is 11. Value is selected by the incremenation
                # of stroke in the for loop above
        

################################### main test, varying current for fixed stroke positions #############################################

    def data_aquire_main(self): # for protoype use fixed current levels and stroke lengths, could be modified to make those values customisable
        
        for stroke_len in (8,11,14): # 8, 11, 14 mm stroke lengths
            
            self.motor.moveto(stroke_len)
            
            with open('./data/main_loop_results' + str(stroke_len) + str('.csv'), 'w', newline='') as csv_file:
                
                csv_writer = csv.writer(csv_file, delimiter=',') # create writing object
                
    #             for x in stroke_len:
    #                 self.motor.move(x)
                # will save each stroke length to individal csv file and then plot them all on the same chart
                
                self.power.set_voltage(12)
                
                for i in range(2,17,1): #start,stop,step, 2-16 (excludes 17) in steps of 1
                    time.sleep(1) # this is needed as the current cannot be set immediately after the power is turned off
                    self.power.set_current(i/20) # /20 to get 0.1 etc current values, and half steps like 0.15A
                    time.sleep(.5)
                    self.power.output('True')
                    time.sleep(1)
                    force = self.reading.get_force(10) # collects the force value from 10 reading average
                    self.power.output('False')
                    csv_writer.writerow([str(i/20), str(force)]) # writes the current and force measured to the csv
                                                                # has to be inside arrary brackets, so as one argument
        self.motor.moveto(0) # reset position

################################### plotting #############################################
        
    def create_vars(self, num): # needed for main loop plotting
        with open('./data/main_loop_results' + str(num), 'r') as csv_file:
                csv_reader = csv.reader(csv_file) # data put into csv_reader object
                
                # create empty lists to add data to in python from the csv file
                current = []
                force = []
                
                # parse over data by iterating over the lines in the csv_reader
                for line in filter(None, csv_reader): # ignore the empty lines
                    col1 = float(line[0]) # collumn variables read value from respective col for each line
                    col2 = float(line[1]) # they are converted to floats for matplotlib to plot
                    
                    current.append(col1) # adding csv vals to the variables for the plots
                    force.append(col2)
        return current, force # returns the current and force that can be assigned to vars in later function
                
    def plot(self, which):
            
        if which == 'main':
                
            i1, f1 = self.create_vars(8)
            i2, f2 = self.create_vars(11)
            i3, f3 = self.create_vars(14)

            plt.plot(i1,f1, marker='s', color='r', label='x=8mm') # markers red squares, with line
            plt.plot(i2,f2, marker='s', color='b', label='x=11mm')
            plt.plot(i3,f3, marker='s', color='g', label='x=14mm')
            
            plt.title('Current (A) vs. Force from Solenoid (N)')
            plt.xlabel('Current (A)')
            plt.ylabel('Force (N)')
            plt.tight_layout()
            plt.grid(True)
            plt.legend()
            plt.savefig('./plots/main_plot.png')
        
        elif which == 'cal':
            
            with open('./data/cal_loop_results.csv', 'r') as csv_file: #importing data from csv file
                csv_reader = csv.reader(csv_file) #putting data into object csv_reader
                  
                set_force = [] #creating empty lists for the data
                hx711_readings = []
                
                ##parsing the data by iterating over the lines in the csv_reader##

                for line in filter(None, csv_reader): # filter parameter removes empty lines, prevents error
                    col2 = float(line[1]) #creating collumn vars which read value for each iteration
                    col3 = float(line[2]) #converting the values read from the csv file to type float, avoiding plotting error
                        # kept plotting data in wrong order, giving appearance of straight lines, solved via changing type to float
                
                    set_force.append(col2) #adding the values to plot vars
                    hx711_readings.append(col3)
           
                x = set_force # Ease of use
                y = hx711_readings 
                #print(*set_force, sep = "\n") # prints list stacked in terminal
                
                ##plotting a scatter graph of the measured data##
                plt.scatter(x, y, marker='x', color='r')#setting markers to red crosses
                plt.title('Force from Solenoid (N) vs. average hx711 reading')
                plt.xlabel('Force (N)')
                plt.ylabel('hx711 readings')
                plt.tight_layout()
                plt.grid(True)
                plt.savefig('./plots/cal_plot.png') # put a folder called plots in the same directory as the code
                #plt.show()
				
        elif which == 'fdx': # plotting the force vs stroke length csv file
            with open('./data/fdx_loop_results.csv', 'r') as csv_file: #importing data from csv file
                csv_reader = csv.reader(csv_file) #putting data into object csv_reader
                      
                force = [] #creating empty lists for the data
                dis = []
                
                ##parsing the data by iterating over the lines in the csv_reader##

                for line in filter(None, csv_reader): # filter parameter removes empty lines, prevents error
                    col1 = float(line[0]) #creating collumn vars which read value for each iteration
                    col2 = float(line[1]) #converting the values read from the csv file to type float, avoiding plotting error
                        # kept plotting data in wrong order, giving appearance of straight lines, solved via changing type to float
                
                    dis.append(col1) #adding the values to plot vars
                    force.append(col2)
           
                x = dis # Ease of use
                y = force 
                
                ##plotting a scatter graph of the measured data##
                plt.scatter(x, y, marker='x', color='r')#setting markers to red crosses
                plt.title('Force from Solenoid (N) vs. stroke length (mm)')
                plt.xlabel('stroke length (mm)')
                plt.ylabel('Force (N)')
                plt.tight_layout()
                plt.grid(True)
                plt.savefig('./plots/fdx_plot.png') # put a folder called plots in the same directory as the code
                #plt.show()
        else:
            print('wrong plot name')
                
            
################################### zeroing method for calibration #########################################################
    
    def gauge(self):
        #zero_val = 77280 # from best case calibration run
        
        zero_val = 80000.0 # type float
        
        ub = (zero_val)*1.05
        lb = (zero_val)*0.95

        # Looking for 76,000 < curr_val < 84,000 or curr_val = 80,000
        while True:
            curr_val = self.measure0() # get the current value of the hx711, with solenoid off
         
            # curr_val needs to be within 5% of zero_val
            if float(curr_val) > ub:
                #print('To High')
                return 'to high', str(curr_val)
            
            elif float(curr_val) < lb:
                #print('To low')
                return 'to low', str(curr_val)
            
            elif float(curr_val) == zero_val or (float(curr_val) > lb)and(float(curr_val) < ub):
                #print(curr_val)
                print('zeroed')
                return 'zeroed' , str(curr_val)
                break
        
#     def zero_click():
#         while True:
#             code, curr_val = self.gauge()
#             #print(code)
#             if code == 'zeroed':
#                 print(code + '  ' + curr_val)
#                 break
               
################################### GPIO cleanup function for error prevention #############################################
     
    def clean():
        GPIO.cleanup()
        
################################### Force vs Stroke length test loop #############################################        

    def data_aquire_fdx(self):
        self.power.set_voltage(14)
        time.sleep(.5)
        self.power.set_current(0.874) # 11W
                        
        with open('./data/fdx_loop_results.csv', 'w', newline='') as csv_file:
            
            for stroke_len in range(1,19,1): # 1mm to 18mm every 1mm
                self.motor.moveto(stroke_len)
                
                csv_writer = csv.writer(csv_file, delimiter=',') # create writing object      
                    
                time.sleep(1) # this is needed as the current cannot be set immediately after the power is turned off
                self.power.output('True')
                time.sleep(1)
                force = self.reading.get_force(10) # collects the force value from 10 reading average
                self.power.output('False')
                time.sleep(.5)
                csv_writer.writerow([str(stroke_len), str(force)]) # writes the force and displacement
                                                                
        self.motor.moveto(0) # reset position
    




#example        
#test = loop_util()
#test.data_aquire_fdx()
#test.plot('fdx')

# test.data_aquire_main()
# 
# test.plot_main()




