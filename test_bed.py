import tkinter as tk
import time
from PIL import ImageTk,Image # used for the images, Pillow library, Process Image Library

import looputility

###################### create top level looputil object  ######################

util = looputility.loop_util()

###################### create variables ######################

HEIGHT = 700
WIDTH = 800

###############################################################################
################################## functions ##################################
###############################################################################


################## function for updating the status window ##################

def status(text):
    textbox.config(state='normal') # make the text box writable using .config
    textbox.insert(1.0, text + '\n') # put new line after statement
    textbox.config(state='disabled')
    
################## Function for resizing the plot image ##################
    
def resize(x): # to resize the plots from matplotlib down 25%, created for use with the calibration function


#'/home/pi/Documents/Project/Classes/plots/cal_plot.png'
    
    plot = Image.open(x)

    #resize the image to scale 75%
    dim = plot.size # size is a tuple (width,height)
    
    #extract dimensions as x and y
    x ,y = dim
    
    s_x = x*0.75 
    s_y = y*0.75 
    
    # apply to original dimensions to get resized ver
    resized = plot.resize((int(s_x),int(s_y)), Image.ANTIALIAS)

    #create the image as an object from the resized version
    resized_plot = ImageTk.PhotoImage(resized)
    new_pathname = './plots/resized_' + str(x) + '.png'
    resized.save(new_pathname) # saves a resized version of the plot inputted
    
    return new_pathname #returns the pathname of the resized image

###################### click functions ########################
# starts the test bed and and updates the status window

def start_cal_click():
    status('Test Started') # updates the status window
    util.data_aquire_cal(1) # uses the data aquire method from loop util for 1 loop, for calibrating the load cell
                        # this will take some time to complete
def start_main_click():
    util.data_aquire_main()
    
def zero_click():
    while True:
        code, curr_val = util.gauge()
        #print(code)
        zero_text.insert(1.0, code + '  ' + curr_val)
        #config(text = code + '  ' + curr_val)
        if code == 'zeroed':
            break
    
###################### Function to add Label for plots in GUI ########################
#GUI

def show_plots_click(path, plot): # displays the plots for calibration, datasheet or the main loop
    #path= image path name, plot= main or cal depending on button pressed
    #decides which branch of the plot method to use
    if plot == 'cal':
        util.plot('cal') # create the plots from the data
        #display the datasheet graph if we are running the calibration#
        datasheet_image = Image.open('./plots/force_stroke_character_datasheet_resized.png')
        datasheet_photo = ImageTk.PhotoImage(datasheet_image)
        #images found in folder plots, which is in code folder

        d_label = tk.Label(plots_frame, image=datasheet_photo)
        d_label.datasheet_image = datasheet_photo
        d_label.place(anchor='ne', relx=1, rely=0.1) # places plot in top left of label, bottom left of canvas
        #placing the datasheet graph into the plot window
        
        new_path = resize(path) # resize created plots for displaying, and collect pathname of resized plot
        
    elif plot =='main':
        util.plot('main')
        new_path = resize(path) # resize the plot, far to big for window
    else:
        print('incorrect plot name')
    
    measured_image = Image.open(new_path) #image opened has just been created by plot() and resized by resize()
    measured_photo = ImageTk.PhotoImage(measured_image)
    #opening the image, making it displayed in the tkinter window.

    m_label = tk.Label(plots_frame, image=measured_photo)
    m_label.measured_image = measured_photo   # to avoid image being destroyed by python garbage collection
                                              #add the extra reference to label highlight ****
    if plot =='cal':
        m_label.place(anchor='ne', relx=0.6, rely=0) # placing cal_plot or main_plot in different locations
    else:
        m_label.place(anchor='nw', relx=0.2, rely=0)

    

################## GUI #########################################
################################################################
################## Root and Canvas Creation ####################
    
root = tk.Tk()
root.title('Linear Actuator Test Bed')

canvas = tk.Canvas(root, height=HEIGHT, width=WIDTH)
canvas.pack()

###################### Buttons Toolbar ########################

upper_frame = tk.Frame(root, bg='#787878')
upper_frame.place(anchor='n', relx=0.5, relheight=0.1, relwidth=1)


startcal_button = tk.Button(upper_frame, font=('consolas',12), text='Start Calibration',
                         bg='green', fg='white', bd=5, relief='groove',
                         command= lambda: start_cal_click())
                         
startcal_button.place(anchor='nw', relx=0, relwidth=0.25, relheight=1)
# this button starts the test process and when clicked cannot be stopped,
# and also will take some time to complete


pltcal_button = tk.Button(upper_frame, font=('consolas',12), text='Plot Calibration', bg='orange', fg='black', bd=5, relief='groove', 
                             command=lambda: show_plots_click('./plots/cal_plot.png', 'cal') ) #lambda to stop it being called upon running

pltcal_button.place(anchor='nw', relx=0.25, relwidth=0.25, relheight=1)
# this button plots the data from the csv file created by the testing process,
# it then displays this plot in the plots frame. For testing purposes the plotting
# function activated by this button was fed a csv file that had already been completed

startmain_button = tk.Button(upper_frame, text='Start Mainloop', bg='blue', fg='white', bd=5, relief='groove', font=('consolas',12),
                             command=lambda: start_main_click())

startmain_button.place(anchor='nw', relx=0.5, relwidth=0.25, relheight=1)

pltmain_button = tk.Button(upper_frame, text='Plot Main', bg='red', fg='white', bd=5, relief='groove', font=('consolas',12),
                           command= lambda: show_plots_click('./plots/main_plot.png', 'main'))

pltmain_button.place(anchor='nw', relx=0.75, relwidth=0.25, relheight=1)


###################### status frame ########################

status_window = tk.Frame(root, bg='#787878')
status_window.place(anchor='n', relx=0.25, rely=0.15, relwidth=0.4, relheight=0.3)
#creating the frame to hold a label that will display information about the test loop

textbox = tk.Text(status_window, bg='white', fg='black', relief='sunken', padx=5, pady=5,
                       width=40, height=10, state='disabled')

textbox.place(anchor='nw', relx=0, rely=0, relwidth=1, relheight=1)

#scrollbar = tk.Scrollbar(status_window, command=status_label.yview)

# textbox = tk.Label(status_window, bg='white', fg='black', relief='sunken', justify='left',
#                    text='test')
# textbox.place(relwidth=1, relheight=1)

###################### zeroing tool frame #######################

zeroing_frame = tk.Frame(root, bg='#787878')
zeroing_frame.place(anchor='n', relx=0.75, rely=0.15, relwidth=0.4, relheight=0.3)
#creating a frame for the widget

zero_text = tk.Text(zeroing_frame, bg='white', fg='black', font=('courier',12), relief='sunken')
zero_text.place(anchor='nw', relx=0.1, rely=0, relwidth=0.8, relheight=0.8)

zero_button = tk.Button(zeroing_frame, bg='red', fg='white', text='zero', bd=5, relief='groove', command=lambda:zero_click())
zero_button.place(anchor='s', relx=0.5, rely=1, relwidth=1)

###################### data presentation frame ########################

plots_frame = tk.Frame(root, bg='#787878')
plots_frame.place(anchor='n', relx=0.5, rely=0.5, relwidth=1, relheight=0.5)
#creating the frame for the graphs

#Graphs are visable when the test has been carried out and the plot button is pressed

########################################################################

root.mainloop()


