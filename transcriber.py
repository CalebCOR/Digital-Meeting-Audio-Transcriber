""" Python Script to transcribe time-stamped audio logs of desktop audio along with creating .wav file recording of transcribed audio

Controls:
'q' - start recording (established in transcriber.py)
'`' - stop recording


"""


import keyboard
import record_audio as record


def main():
    """ Combines Recording + Transcription into a single function """

    previous_event = None
    current_event = None

    start_recording_button = 'q'
    stop_recording_button = '`'

    print("Press " + start_recording_button + " To Begin Recording.")

    while(True):

        previous_event = current_event
        current_event = keyboard.read_event()
        if current_event != previous_event:
            print(current_event)

        if keyboard.is_pressed(start_recording_button):
            break

    
    audio = record.record_audio('test.wav', stop_recording = stop_recording_button)

    audio.close()


main()
