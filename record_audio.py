""" Records audio from recording device set previously by caller using sounddevice.default.device """

import threading
import time
import os
import soundcard as sc
import soundfile as sf
import numpy
import keyboard


def record_audio(save_location, channels=2, stop_recording = '`'):
    """Records audio until a period of silence is detected."""
        
    # local function for use with multithreading
    def add_to_wav(data_array):
        
        print(data_array)

        print(str(data_array.size))
        # Increase volume of wav to normal level
        for x in range(0, data_array.size//2):
            for y in range(0, data_array[x].size):
                # This for loop, should never goes through more than 2 times
                data_array[x][y] *=130
                
        lock.acquire()
        wav_file.write(data_array)
        lock.release()

    
    offload_args=[-1]
    offload = 0
    lock = threading.Lock()
    
    samplerat = 48000
    chunk = 1024
    data_full = numpy.ndarray((chunk,channels), dtype=numpy.float32)
    
    # Time states, initialized with value before while loop
    current_time = 0
    prev_time = 0
    # write_window is the period of time before the wav file is updated (used to offload data before memory issues arise)
    write_window = 40

    speaker = sc.default_speaker()
    microphone = sc.all_microphones(include_loopback=True)
    microphone = microphone[1]

    wav_file = sf.SoundFile(save_location, "w", samplerat, channels)

    print(speaker)
    print(microphone)
    
    ### BEGIN RECORDING ####################################################
    with microphone.recorder(samplerate=samplerat) as mic, speaker.player(samplerate=samplerat) as sp:
        
        current_time = time.time()
        prev_time = current_time

        print("Recording ...")

        while True:
        
            # Check for condition to stop recording
            if keyboard.is_pressed(stop_recording):
                print("breaking")
                break

            # check if data_full should be offloaded to the wav file
            current_time = time.time()
            #print(current_time - prev_time)
            if current_time - prev_time > write_window:
                # Begin offload thread and pass a copy of data_full
                offload_args = [numpy.copy(data_full)]
                offload = threading.Thread(target=add_to_wav, args=offload_args)
                offload.start()

                # reset data_full and set prev_time to equal current_time and 
                prev_time = current_time
                data_full = numpy.ndarray((chunk,channels), dtype=numpy.float32)

            data = mic.record(numframes=chunk)
            data_full = numpy.concatenate((data_full, data), axis=0)

                        
    # After condition for stop recording is True, write rest of data to file + return
    offload_args = [numpy.copy(data_full)]
    offload = threading.Thread(target=add_to_wav, args=offload_args)
    offload.start()

    offload.join()
    #wav_file.close()
        
    return wav_file
