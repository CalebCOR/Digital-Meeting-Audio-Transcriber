# pylint: disable=line-too-long
""" Python Script to transcribe time-stamped audio logs of desktop audio along with creating .wav file recording of transcribed audio"""

import os
import sys
import wave
import datetime

import vosk

CHUNK_SIZE = 1024

def from_wav(p_wav_path, p_output_path, p_vosk_model_path, *, block_duration=0.25, timestamp_duration=10):
    """ Receives a wav filepath string and use kaldi with a vosk model specified by p_vosk_model """

    if not os.path.exists(p_wav_path):
        sys.stderr.write(f"Wav file not found (in transcriber.from_wav()):  {p_wav_path}\n")
        return -1

    with wave.open(p_wav_path, 'rb') as wf:

        sample_rate = wf.getframerate()
        frame_duration = int(sample_rate * block_duration)

        # Get timestamp for the start of the recording (file creation time - duration of recording)
        wav_datetime = os.path.getctime(p_wav_path)
        # Putting the hours, mins, and seconds in their own variables will prob be faster than using datetime methods but doubt it matters
        print(f"\ntesting: {wav_datetime}\t\t{datetime.datetime.fromtimestamp(wav_datetime)}\t\t{wf.getnframes()//sample_rate}\n")
        wav_datetime = datetime.datetime.fromtimestamp(wav_datetime - (wf.getnframes() // sample_rate))
        # time_elapsed is used to keep track of seconds since start of recording
        time_elapsed = datetime.datetime(1,1,1)

        # Create output file and write header text
        with open(p_output_path, 'wt') as output_file:
            output_file.write(f"Transcription of {p_wav_path}. Created on {wav_datetime.strftime("%D %H:%M:%S")}.\n------------------------------------------------------\n")
            recognizer = vosk.KaldiRecognizer(vosk.Model(p_vosk_model_path), sample_rate)

            count = 0
            stop_flag = False
            while not stop_flag:
                data = wf.readframes(frame_duration)
                if len(data) == 0:
                    # Setting count to -1 to trigger a final write to file before breaking out of while
                    count = -1
                    stop_flag = True

                recognizer.AcceptWaveform(data)
                # If num of seconds elapsed since last timestamp update is equal to timestamp_duration
                # Then write new timestamp to file + recognizer output and increment the time objs by 5s
                if (count % int(timestamp_duration/block_duration) == 0 and not count==0 ) or count == -1:
                    output_file.write(f"\n{wav_datetime.strftime("%H:%M:%S")}, {time_elapsed.strftime("%H:%M:%S")} - ")
                    # Using python iterator slice functionality for this since the returned JSON isn't complex
                    output_file.write(f"{recognizer.Result()[14:-3]} ")
                    # Increment datetime objects by timestamp_duration seconds``
                    delta = datetime.timedelta(seconds=timestamp_duration)
                    wav_datetime = wav_datetime + delta
                    time_elapsed = time_elapsed + delta

                count += 1

            output_file.write("\n\nEnd of file. Have a good day.")

    return 1
