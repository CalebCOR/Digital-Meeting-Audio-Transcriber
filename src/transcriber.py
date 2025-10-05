# pylint: disable=line-too-long
""" Python Script to transcribe time-stamped audio logs of desktop audio along with creating .wav file recording of transcribed audio"""

import os
import sys
import wave
import datetime

import vosk

import outputs

CHUNK_SIZE = 1024

def from_wav(p_wav_path, p_output_path, p_vosk_model_path, *, block_duration=0.25, timestamp_duration=10):
    """ Receives a wav filepath string and use kaldi with a vosk model specified by p_vosk_model """

    if not os.path.exists(p_wav_path):
        sys.stderr.write(f"Wav file not found (in transcriber.from_wav()):  {p_wav_path}\n")
        return -1
    

    with wave.open(p_wav_path, 'rb') as wf:

        sample_rate = wf.getframerate()
        frame_duration = int(sample_rate * block_duration)

        
        # wav_datetime is timestamp for the start of the recording (file creation time - duration of recording)
        # time_elapsed is used to keep track of seconds since start of recording
        # NOTE: Putting only the used hours, mins, and seconds in their own variables will prob be faster than using datetime methods but doubt it would make a noticeable difference
        wav_datetime = os.path.getctime(p_wav_path)
        wav_datetime = datetime.datetime.fromtimestamp(wav_datetime - (wf.getnframes() // sample_rate))
        time_elapsed = datetime.datetime(1,1,1)

            
        # Get file type to determine output file format
        file_type = p_output_path.split('.')[-1]
        if file_type not in outputs.type_outputs:
            sys.stderr.write(f"Invalid transcription file type (in transcriber.from_wav()):  .{file_type}\n")
            return -2
        header = f"Transcription of {p_wav_path}. Created on {wav_datetime.strftime("%D %H:%M:%S")}."
        output_func = outputs.type_outputs[file_type]


        with open(p_output_path, 'wt') as output_file:
            
            recognizer = vosk.KaldiRecognizer(vosk.Model(p_vosk_model_path), sample_rate)
            
            # Begin transcription and writing to output file
            count = 0
            stop_flag = False
            first_through = True
            
            while not stop_flag:

                data = wf.readframes(frame_duration)
                if len(data) == 0:
                    # This is setting count to -1 to trigger a final write to file before breaking out of while
                    count = -1
                    stop_flag = True

                recognizer.AcceptWaveform(data)

                # If num of seconds elapsed since last timestamp update is equal to timestamp_duration,
                # Then write new timestamp to file + recognizer output and increment the time objs by 5s
                if (count % int(timestamp_duration/block_duration) == 0 and not count==0 ) or count == -1:
                    
                    # Using python iterator slice functionality for better time since the returned JSON isn't complex
                    text_string = f"{recognizer.Result()[14:-3]}"

                    if first_through:
                        output_func(output_file, wav_datetime, time_elapsed, timestamp_duration, text_string, header_string = header)
                        first_through = False
                    else:
                        output_func(output_file, wav_datetime, time_elapsed, timestamp_duration, text_string)

                    # Increment datetime objects by timestamp_duration seconds``
                    delta = datetime.timedelta(seconds=timestamp_duration)
                    wav_datetime = wav_datetime + delta
                    time_elapsed = time_elapsed + delta

                count += 1

            # Perform final call to output_func
            footer = "\n\nEnd of transcription. Have a good day."
            output_func(output_file, wav_datetime, time_elapsed, 0, '', footer_string=footer)

    return 1
