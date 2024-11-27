import serial
import time
import snp
from snp import snapper 
import csv
import shares

ser = serial.Serial(port='COM3',baudrate=115200,timeout=1)

import sys

## New class called SAAFront
class SAAFront:
    '''
    @brief      A finite state machine to control windshield wipers.
    @details    This class implements a finite state machine to control the
                operation of windshield wipers.
    '''
    
## Constant defining State 0 - Initialization
    S0_INIT       = 0    
    
## Constant defining State 1 - Trial
    S1_TRIAL      = 1    
    
## Constant defining State 2 - Break
    S2_BREAK      = 2 
    
## Constant defining State 3 - Retention Start
    S3_RETENTION_START  = 3
    
## Constant defining State 4 - Retention Test 
    S4_RETENTION_TEST =4
 
## Constant defining State 5 - End
    S5_END =5
    
      
    def __init__(self, test_type, experimenter_type): #input parameters: 
        #test_type is KR (1) or KP(2) and experimenter tablet (3) or human (4)
        '''
        @brief          Creates an  object.

        '''
        
## The state to run on the next iteration of the task.
        self.state = self.S0_INIT
        
        self.runs = 0

        self.interval = 1 
## The timestamp for the first iteration
        self.start_time = time.time()
     
## The "timestamp" for when the task should run next
        self.next_time = self.start_time + self.interval
        
        self.counter =0
        
        self.trial_total = 200 # trial limit
        self.trial_totalr = 205 #Retention trial limit
        
        self.avglist = []
        
        self.trialnumber = []
        
        self.zonenumber = []
        
        self.study_param = []

        
        self.mycam = snp.snapper() #create camera object
        time.sleep(1)
        self.mycam.setup() #initialize camera
        time.sleep(1)
        self.mycam.blank() #take reference camera picture
        time.sleep(1)
        
        self.TrialStatus = 0
        
        self.current_time = 0
        self.present_time=0
        
        self.fcount = 0
        self.firsttrial=1
        
        self.experimenter = experimenter_type
        self.test_type = test_type
        
        self.feedbacklist=[]
       
        

        
    def run(self):
        '''
        @brief      Runs one iteration of the task
        '''
        self.curr_time = time.time()
        if self.curr_time > self.next_time:
            
            if(self.state == self.S0_INIT):
                if ser.read().decode('ascii') == "s": # if s received from 
                #backend, commence
                        print('Intro Message ')  
                        time.sleep(30)
                        self.study_param.append(self.experimenter)
                        self.study_param.append(self.test_type)
                        self.transitionTo(self.S1_TRIAL)
                else:
                    self.transitionTo(self.S0_INIT)


                            
            elif(self.state == self.S1_TRIAL):# Run State 1 Code
                if self.counter < self.trial_total: #if trial limit not 
                #exceeded
                
                    if ser.read().decode('ascii') == "f": #if f received
                    #from backend
                        print('"Break time started"')
                        self.transitionTo(self.S2_BREAK) #transition to 
                        #break state
                    else:
                        status= "t" 
                        ser.write(str(status).encode('ascii')) #send t to
                        #backend indicating trial started
                        time.sleep(1)
                        print('"Trial Start"')
                        time.sleep(7) 
     
                        thing = self.mycam.curnt()  #take puck picture
                        completion = "v"
                        ser.write(str(completion).encode('ascii')) #send v to 
                        #backend to indicate pic taken
                        print('"Trial Over"')
                        time.sleep(4)
                        
                        if thing is None: #if no changes detected 
                        #(puck not on board)
                            self.Ymin = -1 #set pixel x and y variables to
                            #arbitrary -1
                            self.Ymax = -1
                            self.Xmin = -1
                            self.Xmax = -1
                        else:
                            self.Xmin = thing[0]
                            self.Xmax = thing[1]
                            self.Ymin = thing[2]
                            self.Ymax = thing[3]
                            
                        self.counter += 1
                        print('Trial fin : '+ str(self.counter)) 
                        self.trialnumber.append(self.counter) #saves trial 
                        #number to list
                        self.Yavg = (self.Ymin + self.Ymax) * .5 #average max 
                    #and min position of pixel changes to locate where puck is
                        self.avglist.append(self.Yavg)
                            
         
                        if self.Yavg>= 193.5 and self.Yavg<209.5: #if y 
                        #averaged value is in this region
                            self.zonenumber.append(1) #append this zone value 
                            print('z: 1')
                            ser.write(('a').encode('ascii')) #send specific
                            #value to backend
                            if self.firsttrial==1: #if this is very first trial
                                self.fcount=1 #set feedback counter to 1
                                self.firsttrial=0 #set conditional value to 0 
                                #so this conditional statement is never 
                                #entered again 
                            self.fcount= self.fcount -1 #subtract 1 from 
                            #feedback counter
                            if self.fcount==0:
                                self.fcount=3 #reset counter
                                if self.test_type == 1: #if input parameter
                                #is KR feedback
                                    print ('"KR: Your puck is in Zone 1"')
                                else:  #if input parameter isn't KR feedback,
                                #then it must be KP feedback
                                    print ('"KP: Push harder"')

                        elif self.Yavg>=209.5  and self.Yavg<225.5:
                            self.zonenumber.append(2)
                            print('z: 2')
                            ser.write(('b').encode('ascii'))
                            if self.firsttrial==1:
                                self.fcount=1
                                self.firsttrial=0
                            self.fcount= self.fcount -1
                            if self.fcount==0:
                                self.fcount=3
                                if self.test_type == 1:
                                    print ('"KR: Your puck is in Zone 2"')
                                else:
                                    print ('"KP: Push harder"')
                            
                           
                        
                        elif self.Yavg>=225.5  and self.Yavg<242:
                            self.zonenumber.append(3)
                            print('z: 3')
                            ser.write(('c').encode('ascii'))
                            if self.firsttrial==1:
                                self.fcount=1
                                self.firsttrial=0
                            self.fcount= self.fcount -1
                            if self.fcount==0:
                                self.fcount=3
                                if self.test_type == 1:
                                    print ('"KR: Your puck is in Zone 3"')
                                else:
                                    print ('"KP: Push harder"')
                            
                            
                            
                            
                        elif self.Yavg>=242  and self.Yavg<258.5:
                            self.zonenumber.append(4)
                            print('z: 4')
                            ser.write(('d').encode('ascii'))
                            if self.firsttrial==1:
                                self.fcount=1
                                self.firsttrial=0
                            self.fcount= self.fcount -1
                            if self.fcount==0:
                                self.fcount=3
                                if self.test_type == 1:
                                    print ('"KR: Your puck is in Zone 4"')
                                else:
                                    print ('"KP: Push harder"')
                            
                            
                            
                        elif self.Yavg>=258.5  and self.Yavg<276:
                            self.zonenumber.append(5)
                            print('z: 5')
                            ser.write(('e').encode('ascii'))
                            if self.firsttrial==1:
                                self.fcount=1
                                self.firsttrial=0
                            self.fcount= self.fcount -1
                            if self.fcount==0:
                                self.fcount=3
                                if self.test_type == 1:
                                    print ('"KR: Your puck is in Zone 5"')
                                else:
                                    print ('"KP: Push harder"')
                            
                            
                            
                        elif self.Yavg>=276  and self.Yavg<311.5:
                            self.zonenumber.append('G')
                            print('z: G')
                            ser.write(('f').encode('ascii'))
                            if self.firsttrial==1:
                                self.fcount=1
                                self.firsttrial=0
                            self.fcount= self.fcount -1
                            if self.fcount==0:
                                self.fcount=3
                                if self.test_type == 1:
                                    print ('"KR: You reached the goal zone.\
                                           Good job!"')
                                else:
                                    print ('"KP: You reached the goal zone. \
                                           Good job!"')
                            
                            
                            
                        elif self.Yavg>=311.5  and self.Yavg<330:
                            self.zonenumber.append(6)
                            print('z: 6')
                            ser.write(('g').encode('ascii'))
                            if self.firsttrial==1:
                                self.fcount=1
                                self.firsttrial=0
                            self.fcount= self.fcount -1
                            if self.fcount==0:
                                self.fcount=3
                                if self.test_type == 1:
                                    print ('"KR: Your puck is in Zone 6"')
                                else:
                                    print ('"KP: Push softer"')
                            
                            
                            
                        elif self.Yavg>=330  and self.Yavg<349.5:
                            self.zonenumber.append(7)
                            print('z: 7')
                            ser.write(('h').encode('ascii'))
                            if self.firsttrial==1:
                                self.fcount=1
                                self.firsttrial=0
                            self.fcount= self.fcount -1
                            if self.fcount==0:
                                self.fcount=3
                                if self.test_type == 1:
                                    print ('"KR: Your puck is in Zone 7"')
                                else:
                                    print ('"KP: Push softer"')
                            
                            
                            
                        elif self.Yavg>=349.5  and self.Yavg<368:
                            self.zonenumber.append(8)
                            print('z: 8')
                            ser.write(('i').encode('ascii'))
                            if self.firsttrial==1:
                                self.fcount=1
                                self.firsttrial=0
                            self.fcount= self.fcount -1
                            if self.fcount==0:
                                self.fcount=3
                                if self.test_type == 1:
                                    print ('"KR: Your puck is in Zone 8"')
                                else:
                                    print ('"KP: Push softer"')
                            
                            
                            
                        elif self.Yavg>=368  and self.Yavg<388:
                            self.zonenumber.append(9)
                            print('z: 9')
                            ser.write(('j').encode('ascii'))
                            if self.firsttrial==1:
                                self.fcount=1
                                self.firsttrial=0
                            self.fcount= self.fcount -1
                            if self.fcount==0:
                                self.fcount=3
                                if self.test_type == 1:
                                    print ('"KR: Your puck is in Zone 9"')
                                else:
                                    print ('"KP: Push softer"')
                            
                            
                            
                        elif self.Yavg>=388  and self.Yavg<408.5:
                            self.zonenumber.append(10)
                            print('z: 10')
                            ser.write(('k').encode('ascii'))
                            if self.firsttrial==1:
                                self.fcount=1
                                self.firsttrial=0
                            self.fcount= self.fcount -1
                            if self.fcount==0:
                                self.fcount=3
                                if self.test_type == 1:
                                    print ('"KR: Your puck is in Zone 10"')
                                else:
                                    print ('"KP: Push softer"')
                            
                            
                            
                        elif self.Yavg== -1:
                            self.zonenumber.append(-1)
                            print('z: no puck')
                            ser.write(('l').encode('ascii'))
                            if self.firsttrial==1:
                                self.fcount=1
                                self.firsttrial=0
                            self.fcount= self.fcount -1
                            if self.fcount==0:
                                self.fcount=3
                                if self.test_type == 1:
                                    print ('"KR: No puck was detected"')
                                else:
                                    print ('"KP: No puck was detected"')
                            
                            
                            

                        elif self.Yavg< 193.5:
                            self.zonenumber.append(-2)
                            print('z: out front')
                            ser.write(('m').encode('ascii'))
                            if self.firsttrial==1:
                                self.fcount=1
                                self.firsttrial=0
                            self.fcount= self.fcount -1
                            if self.fcount==0:
                                self.fcount=3
                                if self.test_type == 1:
                                    print('"KR: Your puck is out of bounds \
                                          before the zones"')
                                else:
                                    print('"KP: Push a lot harder"')
                            
                            
                        elif self.Yavg> 408.5:
                            self.zonenumber.append(-3)
                            print('z: out back')
                            ser.write(('n').encode('ascii'))
                            if self.firsttrial==1:
                                self.fcount=1
                                self.firsttrial=0
                            self.fcount= self.fcount -1
                            if self.fcount==0:
                                self.fcount=3
                                if self.test_type == 1:
                                    print('"KR: Your puck is out of bounds \
                                          after the zones"')
                                else:
                                    print('"KP: Push a lot softer"')
                            
     

                        time.sleep(6) # delay for experimenter picking up puck
                        

                        if ser.read().decode('ascii') == "f": #if button 
                        #pressed message received
                            print('"Break time started"')
                            self.transitionTo(self.S2_BREAK)

                        self.transitionTo(self.S1_TRIAL) #t
                else:
                    print('Trials Complete')
                    self.transitionTo(self.S3_RETENTION_START)
  
            
            elif(self.state == self.S2_BREAK):
                if ser.read().decode('ascii') == "f":
                    print('"Break time Over"')
                    time.sleep(3)
                    self.transitionTo(self.S1_TRIAL)
                else:
                    self.transitionTo(self.S2_BREAK)
                        
            
                    
            elif(self.state == self.S3_RETENTION_START):
                ser.write(('r').encode('ascii')) #write message to backend 
                #that retention will soon begin 
                print('retention soon message')
                time.sleep(300) # 5min break
                print('retention starting message ')
                ser.write(('q').encode('ascii')) #write retention beginning
                #now message to backend
                time.sleep(20)
                self.transitionTo(self.S4_RETENTION_TEST)
                
            elif(self.state == self.S4_RETENTION_TEST):
                if self.counter < self.trial_totalr: #if retention trial 
                #limit not exceeded
                        status= "t"
                        ser.write(str(status).encode('ascii')) #write message 
                        #to indicate trial started to backend
                        time.sleep(1)
                        print('"Trial Start"')
                        time.sleep(7) #10
                        thing = self.mycam.curnt()  #take picture
                        completion = "v"
                        ser.write(str(completion).encode('ascii')) #write 
                        #message to indicate trial over to backend
                        print('"Trial Over"')
                        time.sleep(4)
                       
                        if thing is None:
                            self.Ymin = -1
                            self.Ymax = -1
                            self.Xmin = -1
                            self.Xmax = -1
                        else:
                            self.Xmin = thing[0]
                            self.Xmax = thing[1]
                            self.Ymin = thing[2]
                            self.Ymax = thing[3]
                            
                        self.counter += 1
                        print('Trial fin : '+ str(self.counter))
                        self.trialnumber.append(self.counter)
                        
                        self.Yavg = (self.Ymin + self.Ymax) * .5
                        # print(self.Yavg)
                        self.avglist.append(self.Yavg)
                            
                            
                        if self.Yavg>= 193.5 and self.Yavg<209.5:
                            self.zonenumber.append(1)
                            print('z: 1')
                            ser.write(('a').encode('ascii'))
                           

                        elif self.Yavg>=209.5  and self.Yavg<225.5:
                            self.zonenumber.append(2)
                            print('z: 2')
                            ser.write(('b').encode('ascii'))
                                             
                        
                        elif self.Yavg>=225.5  and self.Yavg<242:
                            self.zonenumber.append(3)
                            print('z: 3')
                            ser.write(('c').encode('ascii'))
                            
                            
                        elif self.Yavg>=242  and self.Yavg<258.5:
                            self.zonenumber.append(4)
                            print('z: 4')
                            ser.write(('d').encode('ascii'))
                            
                        elif self.Yavg>=258.5  and self.Yavg<276:
                            self.zonenumber.append(5)
                            print('z: 5')
                            ser.write(('e').encode('ascii'))
                           
                             
                        elif self.Yavg>=276  and self.Yavg<311.5:
                            self.zonenumber.append('G')
                            print('z: G')
                            ser.write(('f').encode('ascii'))
                           
                        elif self.Yavg>=311.5  and self.Yavg<330:
                            self.zonenumber.append(6)
                            print('z: 6')
                            ser.write(('g').encode('ascii'))
                            
                            
                        elif self.Yavg>=330  and self.Yavg<349.5:
                            self.zonenumber.append(7)
                            print('z: 7')
                            ser.write(('h').encode('ascii'))
                            
                        elif self.Yavg>=349.5  and self.Yavg<368:
                            self.zonenumber.append(8)
                            print('z: 8')
                            ser.write(('i').encode('ascii'))
                           
                        elif self.Yavg>=368  and self.Yavg<388:
                            self.zonenumber.append(9)
                            print('z: 9')
                            ser.write(('j').encode('ascii'))
                            
                        elif self.Yavg>=388  and self.Yavg<408.5:
                            self.zonenumber.append(10)
                            print('z: 10')
                            ser.write(('k').encode('ascii'))
                            
                        elif self.Yavg== -1:
                            self.zonenumber.append(-1)
                            print('z: no puck')
                            ser.write(('l').encode('ascii'))
                            

                        elif self.Yavg< 193.5:
                            self.zonenumber.append(-2)
                            print('z: out front')
                            ser.write(('m').encode('ascii'))
                           
                            
                        elif self.Yavg> 408.5:
                            self.zonenumber.append(-3)
                            print('z: out back')
                            ser.write(('n').encode('ascii'))
                           

                        time.sleep(6) # delay for experimenter picking up puck
                        
                        self.transitionTo(self.S4_RETENTION_TEST)
                else:
                    print('Retention Trials Complete') #if limit reached
                    self.transitionTo(self.S5_END)
       

            elif(self.state == self.S5_END):
                self.mycam.clser() #exit camera
                time.sleep(2)
                listdecode = ser.readline().decode('ascii') #read list sent
                #from backend 
                self.listdecode = listdecode
                if listdecode !=0:  #if any key is read
                    slist = listdecode.strip('[]\r\n') #strip special characters
                    sslist= slist.split(',')
                    for n in range (len(sslist)): 
                        self.feedbacklist.append(str(sslist[n])) #append 
                        #previous list members to new list
                ser.close()
                while True:
                    with open('SAAdata.csv','w', newline='') as datafile: 
                        #save data to csv file
                        file = csv.writer(datafile)
                        file.writerow(self.study_param)
                        file.writerows(zip(self.trialnumber, self.zonenumber,\
                                           self.avglist, self.feedbacklist))
                        break
                sys.exit('All Trials have been completed and data recorded')

     
            else:
                pass
            
            self.runs += 1
            
            # Specifying the next time the task will run
            self.next_time = self.next_time + self.interval
    
    def transitionTo(self, newState): #defines transitionTo state
        '''
        @brief      Updates the variable defining the next state to run
        '''
        self.state = newState
        
if __name__=="__main__":
 
    
    task1 = SAAFront(1,4)
    
    for N in range(10000000000):
        task1.run()

