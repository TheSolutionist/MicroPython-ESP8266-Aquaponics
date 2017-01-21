#This program uses an esp8266 ( NodeMCU ) Microcontroller running MicroPython to energize a relay.
#The Relay controls a valve that when closed makes a aquaponic grow bed flood and when open drain.


import machine
import utime


#Creating a Class for my Growbed's Back left right. 
class GrowBed:

    def __init__(self, GB_IO):
        self.fill_time = 15
        self.drain_time = 15
        self.remaining_fill_time = 10
        self.remaining_drain_time = 10
        self.is_draining = True
        self.start_drain_time = 0
        self.start_fill_time = 0
        self.GB_IO = GB_IO

def start_filling(self):
    self.is_draining = False
    self.remaining_drain_time = self.drain_time
    self.GB_IO.high()
    



def start_draining(self):
    self.is_draining = True
    self.remaining_fill_time = self.fill_time
    self.GB_IO.low()


        
    
#Set Grow Bed Pin's then make classes for each bed, then created a list of the newly made class-object
back = GrowBed(machine.Pin(5, machine.Pin.OUT))
left = GrowBed(machine.Pin(4, machine.Pin.OUT))
right = GrowBed(machine.Pin(0, machine.Pin.OUT))
Growbeds = [back, left, right]

#time variables
one_second_in_ms = 1000
previoustime = 0
currenttime = utime.ticks_ms()

while True:
    currenttime = utime.ticks_ms()
    if currenttime - previoustime >= one_second_in_ms:
        print('heartbeat')
        for self in Growbeds:
            if self.is_draining:
                self.remaining_drain_time -= 1
                if self.remaining_drain_time <= 0:
                    start_filling(self)
                    print('now filling')
            else:
                self.remaining_fill_time -= 1
                if self.remaining_fill_time <=0:
                    start_draining(self)
                    print('now draining')
        previoustime = currenttime
        utime.sleep(0.01)
                
            
            
      
    



    
    

