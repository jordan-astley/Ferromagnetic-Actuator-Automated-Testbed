# zeroing function
import looputility

util = looputility.loop_util()

def gauge():
    #zero_val = 77280 # from best case calibration run
    
    zero_val = 80000.0 # type float
    
    ub = (zero_val)*1.05
    lb = (zero_val)*0.95

    # Looking for 76,000 < curr_val < 84,000 or curr_val = 80,000
    while True:
        curr_val = util.measure0() # get the current value of the hx711, with solenoid off
     
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
        

def zero_click():
    while True:
        code, curr_val = gauge()
        print(code)
        if code == 'zeroed':
            print(code + '  ' + curr_val)
            break

zero_click()


# def measure0(): #measure the reading with no force applied
#     x = reading.average_read()
#     return float(x)
# 
# def gauge():
#     
#     #zero_val = 77280 # from best case calibration run
#     
#     zero_val = 80000
#     
#     ub = (zero_val)*1.05
#     lb = (zero_val)*0.95
#     
#     # Looking for 76,000 < curr_val < 84,000 or curr_val = 80,000
#     while True:
#         curr_val = measure0() # get the current value of the hx711, with solenoid off
#      
#         # curr_val needs to be within 5% of zero_val
#         if curr_val > ub:
#             print('To High')
#             
#         elif curr_val < lb:
#             print('To low')
#         
#         elif curr_val == zero_val or (curr_val > lb)and(curr_val < ub):
#                # print('zero found')
#                 print(curr_val)
#                 return(True)
#                 break
# 
# def zeroing():
#     gauge()
#     if gauge() == True:
#         print('zeroed')
                
#         while curr_val > ub:
#             print('To High')
#             if curr_val = zero_val or (curr_val < ub)and(curr_val > lb):
#                 print('zero found')
#                 print(curr_val)
#         
#         while curr_val < lb:
#             print('To low')
#             if curr_val = zero_val or (curr_val > lb)and(curr_val < ub):
#                 print('zero found')
#                 print(curr_val)
            
        
