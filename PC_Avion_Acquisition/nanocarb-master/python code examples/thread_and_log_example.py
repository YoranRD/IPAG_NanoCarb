#!/usr/bin/python3

import _thread
import threading
import example_logger

################################################################################
# global vars...
myVar1 = 0
myLock = None
LOOP_PERIOD = 600 # seconds


################################################################################
def ThreadONE():    

    logger.info("Starting Thread1")
    global myVar1

    while (True):        
        loopTimeLap = datetime.datetime.now()
        logger.info("looping Thread1")

        myLock.acquire()
        try : 
            myVar1 = myVar1 + 1
        finally :      
            myLock.release()     
            
        # loop every 'LOOP_PERIOD' : sleep until remaining time
        remainingTime = LOOP_PERIOD - (datetime.datetime.now() - loopTimeLap).total_seconds()
        time.sleep(remainingTime)


################################################################################
def ThreadTWO():
    logger.info("Starting Thread2")
    global myVar1

    while True :
        myLock.acquire()
        try : 
            if (myVar1 == 100):
                myVar1 = 0
        finally :      
            myLock.release()       


################################################################################
if __name__ == "__main__":
    
    # Logger parameters
    logger = example_logger.setup_logger()
    logger.info("Starting example...")

    # init mutex
    myLock = threading.Lock()
                
    # Start thread ONE     
    try:
        _thread.start_new_thread(ThreadONE, ())
    except:
        logger.critical("Could not start thread")
     
    # Start thread ONE     
    try:
        _thread.start_new_thread(ThreadTWO, ())
    except:
        logger.critical("Could not start thread")
        
    # Start Json commands Websocket server      
    while (True) :
        # Do other stuff
        logger.info("Waiting input from command line ?")
        time.sleep(5)

    logger.critical("Should not reach this point !!")





