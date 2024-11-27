import pyb
from pyb import UART 
import utime
import micropython
import sys


micropython.alloc_emergency_exception_buf(200) #for troubleshooting
myuart = UART(2)
uart3= UART(3,9600)
bButton= pyb.Pin(pyb.Pin.board.PA10, mode=pyb.Pin.IN)
myTimer = pyb.Timer(2, prescaler=79, period=0x7FFFFFFF)
button = 0

class SAA:
    '''
    @brief      A finite state machine to control windshield wipers.
    @details    This class implements a finite state machine to control the
                operation of windshield wipers.
    '''
    
## Constant defining State 0 - Initialization
    S0_INIT             = 0    
    
## Constant defining State 1 - Welcome
    S1_WELCOME    = 1    
## Constant defining State 2 - Receive Data
    S2_RECEIVE_DATA   = 2   
    
## Constant defining State 3 - Trial End
    S3_TRIAL_END    = 3   
    
## Constant defining State 4 - Converting Data
    S4_CONVERTING_DATA    = 4  
    
## Constant defining State 5 - Send KR 
    S5_SEND_KR   = 5    
   
## Constant defining State 6 - Send KP
    S6_SEND_KP   = 6   
    
## Constant defining State 7 - Break
    S7_BREAK   = 7  
    
## Constant defining State 8 - Retention Start
    S8_RETENTION_START = 8   
    
## Constant defining State 9- Retention Test B
    S9_RETENTION_TESTB = 9
    
## Constant defining State 10- Retention Test F
    S10_RETENTION_TESTF =10

## Constant defining State 11- End
    S11_END = 11



    def myCallback(self):
        """Function called by interrupt to set button value to 1 to indicate 
            it has been pressed. 
        @brief          Makes button variable global and set it to 1.
    
        """     
        global button #create global variable
        button = 1
        utime.sleep(.5) #delay in case of toggling

        
    extint = pyb.ExtInt (bButton,                    # Which pin
              pyb.ExtInt.IRQ_FALLING,      # Interrupt on falling edge
              pyb.Pin.PULL_DOWN,           # No pull down resistor activated
              myCallback)                  # Interrupt service routine


    def __init__(self,test_type): #test_type parameter is KR (1) or KP (2)
        '''
        @brief         
        
        '''
        
## The state to run on the next iteration of the task.
        self.state = self.S0_INIT
        

## Counter that describes the number of times the task has run
        self.runs = 0
        
##  The amount of time in milliseconds between runs of the task
        self.interval= int(1e3)
        
## The timestamp for the first iteration
        self.start_time = utime.ticks_us()
        
## The "timestamp" for when the task should run next
        self.next_time = utime.ticks_add(self.start_time, self.interval)
        
        
        self.sentdata=[]
        
        self.counter=0
        
        self.test_type = test_type 
        
        self.fcount = 3
        
        self.totaltrialnumber = 200  # Trial number before Retention trials
        
        self.totaltrialnumberr = 205 # Trial number after Retention trials
        
        self.firsttrial=1 #variable indicating FSM is on its first trial 
        

    def run(self):
        '''
        @brief      Runs one iteration of the task
        '''
        global button
        
        self.curr_time = utime.ticks_us()
        if (utime.ticks_diff(self.curr_time, self.next_time)>=0):
            if(self.state == self.S0_INIT):
                # Run State 0 Code
                self.transitionTo(self.S1_WELCOME) #begins transition

            
            
            elif(self.state == self.S1_WELCOME): #State 1
                # Run State 1 Code
                pyb.delay(10000)
                msg= "s"
                myuart.write(msg) #When in this state, message is sent to 
                #the frontend
                pyb.delay(2000)
                self.sendBluetooth(13); #Number sent to tablet via Bluetooth 
                #for welcome dialogue
                self.transitionTo(self. S2_RECEIVE_DATA )
                
                
            
            elif(self.state == self. S2_RECEIVE_DATA ):
                    if self.counter < self.totaltrialnumber: #if trial max 
                    #not reached 
                        if button== 1 : #if button pressed
                              val= "f"
                              myuart.write(val)  #send val to frontend
                              button = 0 
                              self.sendBluetooth(20) #send number to tablet 
                              #via Bluetooth to play break started dialogue
                              if myuart.any():
                                  clearmsg = myuart.readline().decode('ascii') 
                                  # clear any message frontend may have sent
                              self.transitionTo(self.S7_BREAK)
                        else:  
                            if  myuart.any(): #if message received from 
                            #frontend
                                letter= ord( myuart.read().decode('ascii')) 
                                #get value for character received
                                if letter == 116: # value for letter t 
                                    self.sendBluetooth(22)# message to start 
                                    #the trial started sound on tablet
                                    self.transitionTo(self.S3_TRIAL_END)
                                else:
                                    self.transitionTo(self.S2_RECEIVE_DATA)    
                            else:
                                self.transitionTo(self.S2_RECEIVE_DATA)
                    else:
                        self.transitionTo(self. S8_RETENTION_START)
             
                               
               
                
            elif(self.state == self. S3_TRIAL_END ):
                    if  myuart.any(): #if character received from frontend
                        letter= ord( myuart.read().decode('ascii')) 
                        if letter == 118: # if characer value is 118 (v)
                            self.sendBluetooth(23)  #bluetooth message to
                            #play trial end sound
                            self.transitionTo(self.S4_CONVERTING_DATA)
                        else:
                            self.transitionTo(self.S3_TRIAL_END)
                    else:
                            self.transitionTo(self.S3_TRIAL_END)
                    
                             
                             
                        
                        
                        
            elif(self.state == self. S4_CONVERTING_DATA ):   

                    if  myuart.any(): # if anything received from frontend
                        self.counter += 1
                        self.dist= myuart.readline().decode('ascii') #read key 
                        self.distance= ord(self.dist)#get unicode value of key
                        
                        if(self.test_type==1): #if input parameter was 1 go to
                        #KR trials
                            self.transitionTo(self. S5_SEND_KR )
                        elif(self.test_type==2):  #if input parameter was 2 go
                        #to KP trials
                            self.transitionTo(self. S6_SEND_KP)
                    else:
                        self.transitionTo(self. S4_CONVERTING_DATA)
            

                


            elif(self.state == self.S5_SEND_KR):
                
                    if self.firsttrial==1: # if its the very first trial
                      self.fcount=1 #set the fcount to 1 so that in later line
                      #when it gets subtracted it reaches condition
                      #to give feedback
                      # this is because feedback is given the very first trial,
                      #and every third trial afterwards
                      self.firsttrial=0  #set first trial indicator to 0 so 
                     #that code doesn't enter this conditional statement again 

                    self.fcount= self.fcount -1 # each trial, subtract one 
                    #from counter 
                    if self.fcount==0: #if the feedback counter is 0
                        self.fcount=3 # reset counter 
                        
                        if self.distance == 97: #check what message from 
                        #frontend was 
                            self.sendBluetooth(1); #based on message, send 
                            #Bluetooth message
                            pyb.delay(3000) #delay to give human or tablet 
                            #chance to play audio for feedback
                            self.sentdata.append('Zone 1'); 
                            self.transitionTo(self. S2_RECEIVE_DATA )
                            
                        elif self.distance  == 98:
                            self.sendBluetooth(2);
                            pyb.delay(3000)
                            self.sentdata.append('Zone 2');
                            self.transitionTo(self. S2_RECEIVE_DATA )
                            
                        elif self.distance  == 99:
                            self.sendBluetooth(3);
                            pyb.delay(3000)
                            self.sentdata.append('Zone 3');
                            self.transitionTo(self. S2_RECEIVE_DATA )
                            
                        elif self.distance  == 100:
                            self.sendBluetooth(4);
                            pyb.delay(3000)
                            self.sentdata.append('Zone 4');
                            self.transitionTo(self. S2_RECEIVE_DATA )
                            
                        elif self.distance == 101:
                            self.sendBluetooth(5);
                            pyb.delay(3000)
                            self.sentdata.append('Zone 5');
                            self.transitionTo(self. S2_RECEIVE_DATA )
                            
                        elif self.distance == 102:
                            self.sendBluetooth(11);
                            pyb.delay(3000)
                            self.sentdata.append('GOAL');
                            self.transitionTo(self. S2_RECEIVE_DATA )
                            
                        elif self.distance == 103:
                            self.sendBluetooth(6);
                            pyb.delay(3000)
                            self.sentdata.append('Zone 6');
                            self.transitionTo(self. S2_RECEIVE_DATA )
                            
                        elif self.distance == 104:
                            self.sendBluetooth(7);
                            pyb.delay(3000)
                            self.sentdata.append('Zone 7');
                            self.transitionTo(self. S2_RECEIVE_DATA )
                            
                        elif self.distance == 105:
                            self.sendBluetooth(8);
                            pyb.delay(3000)
                            self.sentdata.append('Zone 8');
                            self.transitionTo(self. S2_RECEIVE_DATA )
                            
                        elif self.distance == 106:
                            self.sendBluetooth(9);
                            pyb.delay(3000)
                            self.sentdata.append('Zone 9');
                            self.transitionTo(self. S2_RECEIVE_DATA )
                            
                        elif self.distance == 107:
                            self.sendBluetooth(10);
                            pyb.delay(3000)
                            self.sentdata.append('Zone 10');
                            self.transitionTo(self. S2_RECEIVE_DATA )
                            
                        elif self.distance == 109 :
                            self.sendBluetooth(12);
                            pyb.delay(3000)
                            self.sentdata.append('Out of Bounds front');
                            self.transitionTo(self. S2_RECEIVE_DATA )
                            
                        elif self.distance == 110 :
                            self.sendBluetooth(24);
                            pyb.delay(3000)
                            self.sentdata.append('Out of Bounds back');
                            self.transitionTo(self. S2_RECEIVE_DATA )
                            
                            
                        elif self.distance == 108:
                            self.sendBluetooth(18);
                            pyb.delay(3000)
                            self.sentdata.append('No puck detected');
                            self.transitionTo(self. S2_RECEIVE_DATA )
                            
                        else:
                            self.transitionTo(self.S5_SEND_KR) 
                    else:
                        self.sentdata.append('NA'); #if no feedback for this 
                        #trial, append NA to list
                        self.transitionTo(self. S2_RECEIVE_DATA )


                
            elif(self.state == self.S6_SEND_KP):
                if self.firsttrial==1: # if its the very first trial
                      self.fcount=1 #set the fcount to 1 so that in later
                      #line when it gets subtracted it reaches condition
                      #to give feedback
                      #this is because feedback is given the very first trial,
                      #and every third trial afterwards
                      self.firsttrial=0 #set first trial indicator to 0 so 
                     #that code doesn't enter this conditional statement again 
                self.fcount= self.fcount -1 # each trial, subtract one from
                #counter 
                if self.fcount==0: #if the feedback counter is 0
                        self.fcount=3 # reset counter 

                        if self.distance== 109: #check what message from 
                        #frontend was 
                            self.sendBluetooth(14); #based on message, send 
                            #Bluetooth message
                            pyb.delay(3000) #delay to give human or tablet 
                            #chance to play audio for feedback
                            self.sentdata.append('too soft');
                            self.transitionTo(self.S2_RECEIVE_DATA)
                            
                        elif self.distance== 97 or self.distance== 98 or \
                             self.distance== 99 or self.distance== 100 or \
                             self.distance== 101 :
                            self.sendBluetooth(16);
                            pyb.delay(3000)
                            self.sentdata.append('soft');
                            self.transitionTo(self.S2_RECEIVE_DATA)
        
                        elif self.distance == 102:
                            self.sendBluetooth(11);
                            pyb.delay(3000)
                            self.sentdata.append('GOAL');
                            self.transitionTo(self.S2_RECEIVE_DATA)
                        
                        elif self.distance== 103 or self.distance== 104 or \
                            self.distance== 105 or self.distance== 106 or \
                            self.distance== 107 :
                            self.sendBluetooth(17);
                            pyb.delay(3000)
                            self.sentdata.append(' hard');
                            self.transitionTo(self.S2_RECEIVE_DATA)

                        elif self.distance== 110:
                            self.sendBluetooth(15);
                            pyb.delay(3000)
                            self.sentdata.append('hard');
                            self.transitionTo(self.S2_RECEIVE_DATA)          
                            
                        elif self.distance== 108 :
                            self.sendBluetooth(18);
                            pyb.delay(3000)
                            self.sentdata.append('No puck detected');
                            self.transitionTo(self.S2_RECEIVE_DATA)
                            
                        else:
                            
                            self.transitionTo(self.S6_SEND_KP)
                else:
                    self.sentdata.append('NA'); #if no feedback for this trial
                    #, append NA to list
                    self.transitionTo(self. S2_RECEIVE_DATA )
 
            
            elif(self.state == self.S7_BREAK):
                if button==1: # only occurs when button pressed again,
                #indicating break is over
                        button = 0
                        val= "f"
                        myuart.write(val) #send message to frontend that break
                    #is over
                        self.sendBluetooth(21) #message sent via Bluetooth to
                        #play break is over dialogue
                        self.transitionTo(self.S2_RECEIVE_DATA)          
                else:
                    pass
                                       
             
             
            elif(self.state == self.S8_RETENTION_START):
                if  myuart.any():
                    letter= ord( myuart.read().decode('ascii'))
                    if letter == 114: #if message received was a r 
                        self.sendBluetooth(25) #send Bluetooth message to play
                        #Retention trials starting soon
                        self.transitionTo(self.S8_RETENTION_START) 
                    if letter == 113: #if message received was a q
                        self.sendBluetooth(26) #send Bluetooth message to play
                        #Retention trials starting now
                        self.transitionTo(self.S9_RETENTION_TESTB)
                else:
                    self.transitionTo(self.S8_RETENTION_START)
                    
            elif(self.state == self.S9_RETENTION_TESTB):
                if self.counter <self.totaltrialnumberr: #if Retention trial 
                #limit not exceeded
                    if  myuart.any(): #if message received
                            letter= ord( myuart.read().decode('ascii'))
                            if letter == 116:  # if the character value 
                            #is for the letter t 
                                self.sendBluetooth(22)# send Bluetooth 
                                #message to play the trial start sound
                                self.transitionTo(self.S10_RETENTION_TESTF)
                    else:
                        self.transitionTo(self.S9_RETENTION_TESTB)
                else:
                    self.transitionTo(self. S11_END)
                
                    
            elif(self.state == self.S10_RETENTION_TESTF): 
                if  myuart.any():  #if message received 
                        letter= ord( myuart.read().decode('ascii'))
                        if letter == 118: # if character value for v
                            self.counter += 1
                            self.sentdata.append('NA') #append NA since 
                            #there's no feedback
                            self.sendBluetooth(23)  # Bluetooth message 
                            #signaling tablet to play trial is over sound
                            self.transitionTo(self.S9_RETENTION_TESTB)

                else:
                    self.transitionTo(self.S10_RETENTION_TESTF)
                
            
                        
            elif(self.state == self.S11_END):
                  pyb.delay(2000)
                  self.sendBluetooth(19)
                  myuart.write('{:}\r\n'.format(str(self.sentdata)) \
                               .encode('ascii')) 
                  #send list of feedback to frontend
                  self.counter = 0;
                  pyb.delay(10000);
                  sys.exit('All trials have been completed.')
 
            else:
                # Invalid state code (error handling)
                pass
  
            self.runs += 1
            
            # Specifying the next time the task will run
            # self.next_time = self.next_time + self.interval
            self.next_time = utime.ticks_add(self.next_time, self.interval)
    
    def transitionTo(self, newState): #defines transitionTo state
        '''
        @brief      Updates the variable defining the next state to run
        '''
        self.state = newState

    #Function to write inputs
    def sendBluetooth(self, number):
        """Function to send character via Bluetooth. 
        @brief          
        @details        
        """   
        uart3.write(chr(number)); 
