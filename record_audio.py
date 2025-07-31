# pylint: disable=line-too-long
""" Records audio from input device pyaudio indices passed via p_device_list and prepares the audio for use with vosk and kaldi at a later point """
# If stereo mix is too quiet or microphone in is too loud, volume mixing can be done in Windows microphone settings (I suspect the other os as well but not sure, this note is mostly intended for me)

import wave
import multiprocessing

import pyaudio
import keyboard
import numpy

CHUNK_SIZE = 1024

def prepare_audio(p_file_name, p_pipe_in, p_num_inputs):
    """ Prepares incoming (via p_pipe_in) audio inputs for vosk in real time. 
        Does the following:
            1)  Mix multiple audio inputs into one stream (number of inputs passed as p_num_inputs)
            2)  Converts stereo audio into mono (optional, will happen if p_to_mono is True)
            3)  Write processed audio stream to a wav file (name of the file determined by p_file_name)
    """

    with wave.open(p_file_name, 'wb') as file_pointer:
        
        file_pointer.setnchannels(1)
        file_pointer.setsampwidth(2)
        file_pointer.setframerate(16000)

        mixed_data = numpy.ndarray((1,), dtype=numpy.int32)

        while p_pipe_in.poll(2):
            # in_data format is (input_data (iterable), sample_rate)
            in_data = p_pipe_in.recv()
            # print(f"p_pipe_in == {in_data[0]}")
            match in_data[0][0]:
                case -5:
                    # End of recording case
                    break

                case -6:
                    # End transmission of audio streams for a time instance (stop mixing and write)
                    mixed_data = mixed_data // p_num_inputs
                    
                    # Clipping values down into the valid 16 bit int range and casting from int16 to bytes
                    mixed_data = numpy.clip(mixed_data, -32768, 32767).astype(numpy.int16)
                    file_pointer.writeframes(mixed_data.tobytes())

                    # Reset variables
                    mixed_data = numpy.ndarray((1,), dtype=numpy.int32)

                case _:
                    # Take avg of each value in input streams to mix together (dividing happens in case -6)

                    # Casting to larger int size to avoid value overflow when adding
                    working_data = numpy.frombuffer(in_data[0], dtype=numpy.int16).astype(numpy.int32)

                    # Avg the different channels to monotize multi-channel audio (this accomodates simultaneous mono and stereo recording)
                    temp = working_data[0::in_data[2]]
                    for x in range(1,in_data[2]):
                        temp = temp + working_data[x::in_data[2]]
                    working_data = temp // in_data[2]

                    # Decimate signal down to 16000 sample rate (this works well for 48khz devices and does pretty good for 41khz, anything divisable by 16khz is good)
                    # Intentionally left downsample_factor as a float for use with numpy.arange
                    downsample_factor = in_data[1] / 16000
                    # If downsample_factor does not have a decimal
                    # Then use python iterable slice format
                    # Else use a for loop with numpy.arange() to get something close enough to 16khz be workable
                    if downsample_factor % 1 == 0:
                        working_data = working_data[0::int(downsample_factor)]
                    else:
                        temp = numpy.ndarray((1,), dtype=numpy.int32)
                        for x in numpy.arange(0, len(working_data), downsample_factor):
                            temp = numpy.append(temp, working_data[int(x)])
                        working_data = temp

                    # Add processed data to mixed_data pool for writing to file
                    mixed_data = mixed_data + working_data

                    # print(f"len of mixed_data:\t{len(mixed_data)}")


def record(p_save_location, p_device_list=(), *, start_button='`', stop_button='`'):
    """ Records audio to file at p_save_location """

    audio = pyaudio.PyAudio()

    streams = {}
    devices = {}

    # Setup device dict
    for x in p_device_list:
        device = audio.get_device_info_by_index(x)
        streams[x] = audio.open(format=pyaudio.paInt16,
                                channels=device['maxInputChannels'],
                                rate=int(device['defaultSampleRate']),
                                input=True,
                                input_device_index=x,
                                frames_per_buffer=CHUNK_SIZE,
                                )
        devices[x] = device

    # Poll untill start_button key is pressed
    # Recording starts the moment the key goes down to prevent late starts or
    print(f"Press '{start_button}' to begin recording\n")
    while not keyboard.is_pressed(start_button):
        pass

    # Begin recording untill stop_button key is pressed
    for x in p_device_list:
        # print("Starting Device #" + str(x))
        streams[x].start_stream()

    # Create pipe and prepare_audio() process for some parallelism
    compute_sender, compute_receiver = multiprocessing.Pipe()
    compute_process = multiprocessing.Process(target=prepare_audio, args=(
        p_save_location, compute_receiver, len(p_device_list)))
    compute_process.start()

    print(f"\nNow recording... ")
    print(f"Press '{stop_button}' to stop recording\n")

    # Record untill stop_button is pressed and stop input streams
    current_stop_key_state = True
    prev_key_state = current_stop_key_state

    ### Record and send inputs for procesing #################################
    while not (current_stop_key_state and not prev_key_state):
        for x in p_device_list:
            # Sample rate and # of channels passed alongside input data to ensure data can be decimated to 16000 properly
            compute_sender.send((streams[x].read(CHUNK_SIZE), int(devices[x]['defaultSampleRate']), devices[x]['maxInputChannels']))
        # signal no more streams to be mixed for time instance
        compute_sender.send(((-6,),))

        # Updating states of the stop_recording key
        prev_key_state = current_stop_key_state
        current_stop_key_state = keyboard.is_pressed(stop_button)

    compute_sender.send(((-5,),))  # signal no more audio streams coming

    # Recording has been stopped, Clean up closables
    print(f"Stopping recording...")
    for x in p_device_list:
        streams[x].stop_stream()
        streams[x].close()
    compute_process.join()
    compute_process.close()
    audio.terminate()

