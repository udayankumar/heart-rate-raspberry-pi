# Simple heart beat reader for Raspberry pi using ADS1x15 family of ADCs and a pulse sensor - http://pulsesensor.com/.
# The code borrows heavily from Tony DiCola's examples of using ADS1x15 with 
# Raspberry pi and WorldFamousElectronics's code for PulseSensor_Amped_Arduino

# Author: Udayan Kumar
# License: Public Domain

import time
# Import the ADS1x15 module.
import Adafruit_ADS1x15


if __name__ == '__main__':

    adc = Adafruit_ADS1x15.ADS1015()
    # initialization 
    GAIN = 2/3  
    curState = 0
    thresh = 525  # mid point in the waveform
    P = 512
    T = 512
    stateChanged = 0
    sampleCounter = 0
    lastBeatTime = 0
    firstBeat = True
    secondBeat = False
    Pulse = False
    IBI = 600
    rate = [0]*10
    amp = 100

    lastTime = int(time.time()*1000)

    # Main loop. use Ctrl-c to stop the code
    while True:
        # read from the ADC
        Signal = adc.read_adc(0, gain=GAIN)   #TODO: Select the correct ADC channel. I have selected A0 here
        curTime = int(time.time()*1000)

        sampleCounter += curTime - lastTime;      #                   # keep track of the time in mS with this variable
        lastTime = curTime
        N = sampleCounter - lastBeatTime;     #  # monitor the time since the last beat to avoid noise
        #print N, Signal, curTime, sampleCounter, lastBeatTime

        ##  find the peak and trough of the pulse wave
        if Signal < thresh and N > (IBI/5.0)*3.0 :  #       # avoid dichrotic noise by waiting 3/5 of last IBI
            if Signal < T :                        # T is the trough
              T = Signal;                         # keep track of lowest point in pulse wave 

        if Signal > thresh and  Signal > P:           # thresh condition helps avoid noise
            P = Signal;                             # P is the peak
                                                # keep track of highest point in pulse wave

          #  NOW IT'S TIME TO LOOK FOR THE HEART BEAT
          # signal surges up in value every time there is a pulse
        if N > 250 :                                   # avoid high frequency noise
            if  (Signal > thresh) and  (Pulse == False) and  (N > (IBI/5.0)*3.0)  :       
              Pulse = True;                               # set the Pulse flag when we think there is a pulse
              IBI = sampleCounter - lastBeatTime;         # measure time between beats in mS
              lastBeatTime = sampleCounter;               # keep track of time for next pulse

              if secondBeat :                        # if this is the second beat, if secondBeat == TRUE
                secondBeat = False;                  # clear secondBeat flag
                for i in range(0,10):             # seed the running total to get a realisitic BPM at startup
                  rate[i] = IBI;                      

              if firstBeat :                        # if it's the first time we found a beat, if firstBeat == TRUE
                firstBeat = False;                   # clear firstBeat flag
                secondBeat = True;                   # set the second beat flag
                continue                              # IBI value is unreliable so discard it


              # keep a running total of the last 10 IBI values
              runningTotal = 0;                  # clear the runningTotal variable    

              for i in range(0,9):                # shift data in the rate array
                rate[i] = rate[i+1];                  # and drop the oldest IBI value 
                runningTotal += rate[i];              # add up the 9 oldest IBI values

              rate[9] = IBI;                          # add the latest IBI to the rate array
              runningTotal += rate[9];                # add the latest IBI to runningTotal
              runningTotal /= 10;                     # average the last 10 IBI values 
              BPM = 60000/runningTotal;               # how many beats can fit into a minute? that's BPM!
              print 'BPM: {}'.format(BPM)

        if Signal < thresh and Pulse == True :   # when the values are going down, the beat is over
            Pulse = False;                         # reset the Pulse flag so we can do it again
            amp = P - T;                           # get amplitude of the pulse wave
            thresh = amp/2 + T;                    # set thresh at 50% of the amplitude
            P = thresh;                            # reset these for next time
            T = thresh;

        if N > 2500 :                          # if 2.5 seconds go by without a beat
            thresh = 512;                          # set thresh default
            P = 512;                               # set P default
            T = 512;                               # set T default
            lastBeatTime = sampleCounter;          # bring the lastBeatTime up to date        
            firstBeat = True;                      # set these to avoid noise
            secondBeat = False;                    # when we get the heartbeat back
            print "no beats found"

        time.sleep(0.005)

