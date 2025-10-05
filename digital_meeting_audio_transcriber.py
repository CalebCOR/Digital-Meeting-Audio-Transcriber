# pylint: disable=line-too-long
""" Records desktop audio (from stereo mix) and microphone audio (from default input) """

import os
import sys
import argparse
import configparser

import pyaudio

sys.path.append('.\\src\\')
import record_audio
import transcriber
import outputs

# Modify the following constants as desired
START_RECORDING = '`'
STOP_RECORDING = '`'
WAV_FILENAME = 'a.wav'
TRANSCRIPTION_FILENAME = 'a.txt'
MODEL_DIRECTORY = 'vosk-model-small-en-us-0.15'
# xxx_DEVICE_NAME_INCLUDES is a string that is searched for in the input device name when choosing recording devices
MICROPHONE_DEVICE_NAME_INCLUDES = 'Microphone'
STEREO_MIX_DEVICE_NAME_INCLUDES = 'Stereo Mix'
# DESIRED_xxx_AUDIO_BACKEND is a string that is matched EXACTLY to the audio backend of the input device
DESIRED_MICROPHONE_AUDIO_BACKEND = 'Windows WASAPI'
DESIRED_STEREO_MIX_AUDIO_BACKEND = 'Windows WASAPI'
# Timestamps in the produced .txt log are added every TRANSCRIPTION_TIMESTAMP_FREQUENCY seconds (default 10 seconds)
TRANSCRIPTION_TIMESTAMP_FREQUENCY = 10


if __name__ == '__main__':
    """ da main function """


    # Parsing config defaults from default_values.ini into variables
    config_parser = configparser.ConfigParser()
    config_parser.read('default_values.ini')
    defaults = config_parser['DEFAULT_VALUES']

    START_RECORDING = defaults['START_RECORDING']
    STOP_RECORDING = defaults['STOP_RECORDING']
    WAV_FILENAME = defaults['WAV_FILENAME']
    TRANSCRIPTION_FILENAME = defaults['TRANSCRIPTION_FILENAME']
    MODEL_DIRECTORY = defaults['MODEL_DIRECTORY']
    MICROPHONE_DEVICE_NAME_INCLUDES = defaults['MICROPHONE_DEVICE_NAME_INCLUDES']
    STEREO_MIX_DEVICE_NAME_INCLUDES = defaults['STEREO_MIX_DEVICE_NAME_INCLUDES']
    DESIRED_MICROPHONE_AUDIO_BACKEND = defaults['DESIRED_MICROPHONE_AUDIO_BACKEND']
    DESIRED_STEREO_MIX_AUDIO_BACKEND = defaults['DESIRED_STEREO_MIX_AUDIO_BACKEND']
    try:
        TRANSCRIPTION_TIMESTAMP_FREQUENCY = int(defaults['TRANSCRIPTION_TIMESTAMP_FREQUENCY'])
    except ValueError:
        print(f'\nInvalid value for TRANSCRIPTION_TIMESTAMP_FREQUENCY in default_values.ini.\n\nPlease make sure TRANSCRIPTION_TIMESTAMP_FREQUENCY in default_values.ini is a number.\nCurrent value: {defaults['TRANSCRIPTION_TIMESTAMP_FREQUENCY']}\n', file=sys.stderr)
        quit()

    # Parsing CLI arguments and updating config defaults
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("-M","--no_mic", action='store_true',   help='Do not include microphone audio input in recording')
    arg_parser.add_argument("-D","--no_desktop", action='store_true',   help='Do not include desktop audio input in recording')
    
    arg_parser.add_argument("-r","--set_recording_name",   help=f"Set the desired name of the audio recording output file (default is {WAV_FILENAME} supported file types are {['wav']})")
    arg_parser.add_argument("-o","--set_output_name",   help=f"Set the desired name of the transcription output file (default is {TRANSCRIPTION_FILENAME} supported file types are {[x for x in outputs.type_outputs]})")
    
    arg_parser.add_argument("-m","--set_mic",   help=f"Set the desired microphone audio device by inputting a string that will be searched for from the names of your available input devices. input is case insensitive (default is '{MICROPHONE_DEVICE_NAME_INCLUDES}')")
    arg_parser.add_argument("-d","--set_desktop",   help=f"Set the desired desktop audio device by inputting a string that will be searched for from the names of your available input devices, input is case insensitive (default is '{STEREO_MIX_DEVICE_NAME_INCLUDES}')")
    arg_parser.add_argument("-mb","--set_mic_backend",   help=f"Set the desired microphone audio backend by inputting a string that will be searched for from the names of your available input devices, input is case insensitive (default is '{DESIRED_MICROPHONE_AUDIO_BACKEND}')")
    arg_parser.add_argument("-md","--set_desktop_backend",   help=f"Set the desired desktop audio backend by inputting a string that will be searched for from the audio backends of your available input devices, input is case insensitive (default is '{DESIRED_STEREO_MIX_AUDIO_BACKEND}')")
    arg_parser.add_argument("-s","--set_model_dir",   help=f"Set the name of the desired speech recognition model directory to use for transcription. The input will searched from the names of available directories inside the models directory, input is case insensitive (default is '{MODEL_DIRECTORY}')")

    args = arg_parser.parse_args()
    

    # Update the config variables with the user's CLI arguments
    if args.set_recording_name:
        WAV_FILENAME = args.set_recording_name
    if args.set_output_name:
        TRANSCRIPTION_FILENAME = args.set_output_name
    if args.set_mic:
        MICROPHONE_DEVICE_NAME_INCLUDES = args.set_mic
    if args.set_desktop:
        STEREO_MIX_DEVICE_NAME_INCLUDES = args.set_desktop
    if args.set_mic_backend:
        DESIRED_MICROPHONE_AUDIO_BACKEND = args.set_mic_backend
    if args.set_desktop_backend:
        DESIRED_STEREO_MIX_AUDIO_BACKEND = args.set_desktop_backend
    if args.set_model_dir:
        MODEL_DIRECTORY = args.set_model_dir
    
    # Searching for user's recognition model name among the directories in .\models\
    # NOTE: This happens so early because this error checking should happen before user does anything
    model_name = -1
    for x in os.listdir('.\\models\\'):

        if os.path.isdir('.\\models\\' + x) \
          and MODEL_DIRECTORY in x:
            model_name = x
            break

    if model_name == -1:
        print(f"\nUnable to find a recognition model in the models directory with '{MODEL_DIRECTORY}' in the name.\n\nPlease make sure your models directory looks like this:\nex.  models/recognition_model_name/(model contents)\n", file=sys.stderr)
        quit()



    a = pyaudio.PyAudio()
    input_devices = []
    
    
    # Get the input devices that will be recorded from and fill input_devices list with device indices
    
    for x in range(a.get_device_count()):
        b = a.get_device_info_by_index(x)

        #TODO when I get around to implementing recording of user determined # of devices turn these 2 flags into a list of flags or something
        desktop_found = False
        mic_found = False
        if args.no_desktop is not True \
          and desktop_found is False \
          and b['maxInputChannels'] == 2\
          and STEREO_MIX_DEVICE_NAME_INCLUDES.upper() in b['name'].upper() \
          and a.get_host_api_info_by_index(b['hostApi'])['name'].upper() == DESIRED_STEREO_MIX_AUDIO_BACKEND.upper():
            
            input_devices.append(b['index'])
            desktop_found = True

        elif args.no_mic is not True \
          and mic_found is False \
          and b['maxInputChannels'] == 2 \
          and MICROPHONE_DEVICE_NAME_INCLUDES.upper() in b['name'].upper() \
          and DESIRED_MICROPHONE_AUDIO_BACKEND.upper() in a.get_host_api_info_by_index(b['hostApi'])['name'].upper():
            
            input_devices.append(b['index'])
            mic_found = True
    

    # Tell the user the recognition model being used
    # NOTE: the recognition model was chosen earlier due to required error handling in the case of no model being found
    print(f"\nThe following recognition model is being used for transcription:")
    print(f"{model_name}")
    print()

    # Tell the user the list of devices being recorded
    # TODO When verbose is included, add backend to the output string, f"{name}, {backend}"
    print(f"The following devices are being recorded:")
    for x in input_devices:
        b = a.get_device_info_by_index(x)
        name = b['name']
        backend = a.get_host_api_info_by_index(b['hostApi'])['name']
        print(f"{name}")
        #print(f"{name}, {backend}")
    print()

    a.terminate()



    # If WAV_FILENAME already exists, will lead to inaccurate timekeeping in transcriber.from_wav()
    if os.path.exists(WAV_FILENAME):
        sys.stderr.write(f"The file '{WAV_FILENAME}' already exists\n")
        response = input("Overwrite?  Y/N ").rstrip("\n").lower()
        if response == 'y':
            print("Overwriting...\n")
            # WAV_FILENAME will be recreated in record_audio.record()
            os.remove(WAV_FILENAME)

        else:
            # This will add '_copy' until a unique wav filename is created in directory
            while os.path.exists(WAV_FILENAME):
                WAV_FILENAME = WAV_FILENAME[:-4] + '_copy' + WAV_FILENAME[-4:]
            print(f"Not overwriting, new file name will be '{WAV_FILENAME}\n")


    # Now doing the same for TRANSCRIPTION_FILENAME
    if os.path.exists(TRANSCRIPTION_FILENAME):
        sys.stderr.write(f"The file '{TRANSCRIPTION_FILENAME}' already exists\n")
        response = input("Overwrite?  Y/N ").rstrip("\n").lower()
        if response == 'y':
            print("Overwriting...\n")
            # TRANSCRIPTION_FILENAME will be recreated in transcriber.from_wav()
            os.remove(TRANSCRIPTION_FILENAME)

        else:
            # This will add '_copy' until a unique transcription filename is created in directory
            while os.path.exists(TRANSCRIPTION_FILENAME):
                TRANSCRIPTION_FILENAME = TRANSCRIPTION_FILENAME[:-4] + '_copy' + TRANSCRIPTION_FILENAME[-4:]
            print(f"Not overwriting, new file name will be '{TRANSCRIPTION_FILENAME}\n")
    


    record_audio.record(WAV_FILENAME, tuple(input_devices), start_button=START_RECORDING, stop_button=STOP_RECORDING)
    print("------------------------------------------------------")
    print("------------  Beginning transcription...  ------------")
    print("------------------------------------------------------")
    transcriber.from_wav(WAV_FILENAME, TRANSCRIPTION_FILENAME, '.\\models\\' + model_name, timestamp_duration=TRANSCRIPTION_TIMESTAMP_FREQUENCY)
    