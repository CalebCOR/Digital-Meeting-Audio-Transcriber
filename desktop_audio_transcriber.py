# pylint: disable=line-too-long
""" Records desktop audio (from stereo mix) and microphone audio (from default input) """

import os
import sys

import pyaudio
import record_audio
import transcriber

# Modify the following constants as desired
START_RECORDING = '`'
STOP_RECORDING = '`'
WAV_FILENAME = 'a.wav'
TRANSCRIPTION_FILENAME = 'a.txt'
MODEL_DIRECTORY = 'vosk-model-small-en-us-0.15'
# INPUT_DEVICE_NAME_INCLUDES is a string that is searched for in the device name
INPUT_DEVICE_NAME_INCLUDES = 'Microphone'
# DESIRED_xxx_AUDIO_BACKEND is a string that is matched EXACTLY to the audio backend of the input device
DESIRED_MICROPHONE_AUDIO_BACKEND = 'Windows WASAPI'
DESIRED_STEREO_MIX_AUDIO_BACKEND = 'Windows WASAPI'
# Timestamps in the produced .txt log are added every TRANSCRIPTION_TIMESTAMP_FREQUENCY seconds (default 10 seconds)
TRANSCRIPTION_TIMESTAMP_FREQUENCY = 10


if __name__ == '__main__':
    """ da main function """

    a = pyaudio.PyAudio()
    input_devices = []

    # Get the input devices that will be recorded from and fill input_devices list with device indices
    for x in range(a.get_device_count()):
        b = a.get_device_info_by_index(x)
        if 'Stereo Mix' in b['name'] and a.get_host_api_info_by_index(b['hostApi'])['name'] == DESIRED_STEREO_MIX_AUDIO_BACKEND:
            """ print(b)
            print(a.get_host_api_info_by_index(b['hostApi'])['name'])
            print() """
            input_devices.append(b['index'])

        elif INPUT_DEVICE_NAME_INCLUDES in b['name'] and a.get_host_api_info_by_index(b['hostApi'])['name'] == DESIRED_MICROPHONE_AUDIO_BACKEND:
            """ print(b)
            print(a.get_host_api_info_by_index(b['hostApi'])['name'])
            print()  """
            input_devices.append(b['index'])

    print(f"\nThe following devices are being recorded:")
    for x in input_devices:
        print(f"{a.get_device_info_by_index(x)['name']}")
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
    transcriber.from_wav(WAV_FILENAME, TRANSCRIPTION_FILENAME, ".\\models\\" + MODEL_DIRECTORY, timestamp_duration=TRANSCRIPTION_TIMESTAMP_FREQUENCY)
