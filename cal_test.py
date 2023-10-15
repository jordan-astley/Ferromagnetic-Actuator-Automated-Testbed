# measures stroke lengths 8mm to 18mm in 1mm increments

# calibrating the force transducer
# commands to move the armature and output the specified current
# recording the hx711 reading
import tkinter as tk
import time
from PIL import ImageTk,Image # used for the images, Pillow library, Process Image Library
import RPi.GPIO as GPIO

import csv
import matplotlib.pyplot as plt

def clean():
    GPIO.cleanup()    
clean()

####################### instantiate the class objects for the sub-systems ######################

import force_transducer
import serialcom
import stepper_motor_class    

#comment this section out for testing GUI
power = serialcom.power_supply()
reading = force_transducer.load_cell()
motor = stepper_motor_classv2.stepper_motor(20, 21, (26,19,13), 1, '8', 16)
# #(self, DIR, STEP, MODE, CW, mstep, EN)

###################### create variables ######################

HEIGHT = 700
WIDTH = 800

###################### operation functions ######################

def set_power(): #setting for 11W power in 14.4 ohm coil
    power.set_voltage(14)
    time.sleep(.1)
    power.set_current(0.874)
    
def measure0(): #measure the reading with no force applied
    power.output('False')
    time.sleep(3)
    x = reading.average_read()
    #print(x)
    return str(x)
    #ensure armature is fully closed, rotate the ballscrew if needed??????
    
def measure(): #return the 'average' function output from hx711 library
    power.output('True')
    time.sleep(3)
    x = reading.average_read()
    power.output('False')
    return str(x)

################## Function for updating the status window ##################

def status(text):
    textbox.config(state='normal') # make the text box writable using .config
    textbox.insert(1.0, text + '\n') # put new line after statement
    textbox.config(state='disabled')
    

###################### Data capture functions ######################

#need to add way to define the file name of the plot and data

def data_aquire(times): #runs the test bed, times is an integer number defines how many loops of aquiring data
    
    time.sleep(1)
    
    set_power() # sets 11W, 14.4 ohm coils
    
    ##force for each of predefined stroke lengths, read from the data sheet##
    force_vals = ['0','4.9','4.165','3.675','3.185','2.695','2.45','2.205','1.96','1.862','1.764','1.715']
    
    with open('./data/cal_loop_results.csv', 'w', newline='') as csv_file: #create csv file called loop_results
        
        csv_writer = csv.writer(csv_file, delimiter=',') # create writing object
        
        for t in range(times): # so data_aquire(5) to repeat the test 5 times
            
            count = 0 # counter for using the specific force_vals list entries, above
            # having the counter inside the for loop resets it each time, so the force vals are read correctly
            
            # measure 0 mm force output @ 0.874A, this will be our 0N point for calibrating the hx711
            # measures 0 force applied to load cell
            motor.moveto(0) 
            time.sleep(1)
            output = measure()
            csv_writer.writerow([str(0),str(force_vals[count]),str(output)])
            count = count + 1
            time.sleep(1)
            
            ##measure from 8mm to 18mm, in 1mm steps##
            for stroke in range(8,19,1): #(start,stop,step)
                motor.moveto(stroke)
                time.sleep(1)
                output = measure()
                csv_writer.writerow([str(stroke),str(force_vals[count]), str(output)])
                count = count + 1
                time.sleep(1)
            
            status('loop ' + str(t) + ' done')
            motor.moveto(0) # reset back to 0
            
            # added write row force_vals, writes the incremented value of force from the force_vals list
            # this means when looking at the .csv file you have comma separated vars of:
            # stroke length, force(N), hx711 average output
            # it should use the correct force values, of which there is 11. Value is selected by the incremenation
            # of stroke in the for loop above
            
###################### Plot function ######################

def plot_cal(): ##Take the data returned from aquire function and plot it##   
    
    
    with open('./data/cal_loop_results.csv', 'r') as csv_file: #importing data from csv file
        csv_reader  = csv.reader(csv_file) #putting data into object csv_reader
          
        set_force = [] #creating empty lists for the data
        hx711_readings = []
        
        ##parsing the data by iterating over the lines in the csv_reader##

        for line in filter(None, csv_reader): # filter parameter removes empty lines, prevents error
            col2 = float(line[1]) #creating collumn vars which read value for each iteration
            col3 = float(line[2]) #converting the values read from the csv file to type float, avoiding plotting error
            
            set_force.append(col2) #adding the values to plot vars
            hx711_readings.append(col3)
   
        x = set_force # Ease of use
        y = hx711_readings 
        #print(*set_force, sep = "\n") # prints list stacked in terminal
        
        
        ##plotting a scatter graph of the measured calibration##
        
        plt.scatter(x, y, marker='x', color='r')#setting markers to red crosses
        
        plt.title('Force from Solenoid (N) vs. average hx711 reading')
        plt.xlabel('Force (N)')
        plt.ylabel('hx711 readings')
        plt.tight_layout()
        plt.grid(True)
        plt.savefig('./plots/cal_plot.png') # put a folder called plots in the same directory as the code
        #plt.show()

# kept plotting data in wrong order, giving appearance of straight lines, solved via changing type to float


################## Function for resizing the plot image ##################
    
def resize(x): # to resize the plots from matplotlib
#'/home/pi/Documents/Project/Classes/plots/cal_plot.png'
    plot = Image.open(x)

    #resize the image to scale 75%
    dim = plot.size # size is a tuple (width,height)
    
    #extract dimensions as x and y
    x ,y = dim
    
    scale_x = (x/4) # 25% of fo the original size
    scale_y = (y/4) # same to y to preserve aspect ratio
    
    s_x = x - scale_x
    s_y = y - scale_y
    
    # apply to original dimensions to get resized ver
    resized = plot.resize((int(s_x),int(s_y)), Image.ANTIALIAS)

    #create the image as an object from the resized version
    resized_plot = ImageTk.PhotoImage(resized)
    resized.save('./plots/resized_cal_plot.png')

###################### Start button click function ########################
# starts the test bed and and updates the status window

def start_click():
    status('Test Started') # updates the status window
    data_aquire(1)
        
###################### Function to add Label for plots in GUI ########################
#GUI

def show_plots(path): # displays the calculated plot and the datasheet
    #plt_button.config(state='disabled') #greys out the button
    
    plot_cal() # create the plots from the data
    
    resize(path) # resize created plots for displaying
    
    time.sleep(1)
    
    measured_image = Image.open('./plots/resized_cal_plot.png') #image opened has just been created by plot_cal()
    measured_photo = ImageTk.PhotoImage(measured_image)
    #opening the image, making it displayed in the tkinter window.

    m_label = tk.Label(plots_frame, image=measured_photo)
    m_label.measured_image = measured_photo #*****
    m_label.place(anchor='ne', relx=0.6, rely=0)
    # to avoid image being destroyed by python garbage collection
    #add the extra reference to label highlight ****
    
    datasheet_image = Image.open('./plots/force_stroke_character_datasheet_resized.png')
    datasheet_photo = ImageTk.PhotoImage(datasheet_image)
    #images found in folder plots, which is in code folder

    d_label = tk.Label(plots_frame, image=datasheet_photo)
    d_label.datasheet_image = datasheet_photo
    d_label.place(anchor='ne', relx=1, rely=0.1) # places plot in top left of label, bottom left of canvas
    #placing the datasheet graph into the plot window


################## GUI #########################################
################################################################
################## Root and Canvas Creation ####################
    
root = tk.Tk()
root.title('Calibration Loop')

canvas = tk.Canvas(root, height=HEIGHT, width=WIDTH)
canvas.pack()

###################### Buttons Toolbar ########################

upper_frame = tk.Frame(root, bg='#787878')
upper_frame.place(anchor='n', relx=0.5, relheight=0.1, relwidth=0.4)


start_button = tk.Button(upper_frame, font=40, text='Start Calibration',
                         bg='green', fg='white', bd=5, relief='groove',
                         command= lambda: start_click())
                         
start_button.place(relx=0, relwidth=0.5, relheight=1)
# this button starts the test process and when clicked cannot be stopped,
# and also will take some time to complete


plt_button = tk.Button(upper_frame, font=40, text='Plot Results', bg='orange', fg='black', bd=5, relief='groove', 
                             command=lambda: show_plots('./plots/cal_plot.png') ) #lambda to stop it being called upon running

plt_button.place(anchor='n', relx=0.75, relwidth=0.5, relheight=1)
# this button plots the data from the csv file created by the testing process,
# it then displays this plot in the plots frame. For testing purposes the plotting
# function activated by this button was fed a csv file that had already been completed

###################### status window ########################

status_window = tk.Frame(root, bg='#787878')
status_window.place(anchor='n', relx=0.5, rely=0.15, relwidth=0.7, relheight= 0.3)
#creating the frame to hold a label that will display information about the test loop

textbox = tk.Text(status_window, bg='white', fg='black', relief='sunken', padx=5, pady=5,
                       width=40, height=10, state='disabled')

textbox.place(anchor='nw', relx=0, rely=0, relwidth=1, relheight=1)

#scrollbar = tk.Scrollbar(status_window, command=status_label.yview)

# textbox = tk.Label(status_window, bg='white', fg='black', relief='sunken', justify='left',
#                    text='test')
# textbox.place(relwidth=1, relheight=1)

###################### data presentation window ########################

plots_frame = tk.Frame(root, bg='#787878')
plots_frame.place(anchor='n', relx=0.5, rely=0.5, relwidth=1, relheight=0.5)
#creating the frame for the graphs

#Graphs are visable when the test has been carried out and the plot button is pressed

########################################################################

root.mainloop()



