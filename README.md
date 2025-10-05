# Digital-Meeting-Audio-Transcriber
By Caleb Corlett, Version 2.0.0 (October 5, 2025)

A Python script to transcribe desktop audio and microphone input, producing a time-stamped transcription and a .wav file of the transcribed audio.

To Run:
1) Make sure the latest version of Python 3 is installed.
2) Install the necessary requirements with `pip install -r requirements.txt` or `python -m pip install -r requirements.txt`.
3) Run `python digital_meeting_audio_transcriber.py` to begin a new recording.

The default_values.ini file has a list of variables that can be modified to make the Digital Meeting Audio Transcriber appropriately fit your needs. This is likely to be required on anything other than Windows.

:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

Vosk Offline Speech Recognition models are used to transcribe the audio to text. The small en-us model (300mb vram required) is included by default. More advanced models can be downloaded from `https://alphacephei.com/vosk/models`. Once downloaded, place the model directory into the \models directory and update the `MODEL_DIRECTORY` variable in default_values.ini with the new model directory or use the `-s` CLI option to set the model directory from the CLI.

The log produced contains the spoken words from the audio along with timestamps for the actual time the words were said (ex. a word said at 1:45pm can be found at the 13:45:00 timestamp) as well as the relative time where the words can be found in the recording (ex. a word said 1 hour, 15 minutes, and 30 seconds into the .wav recording can found at the 01:15:30 timestamp)

Timestamps are placed in the log every 10 seconds by default, can be modified by changing the `TRANSCRIPTION_TIMESTAMP_FREQUENCY` variable in default_values.ini.

The .wav recording is downsampled to 16 kHz sample rate for better use with the transcriber. It is normal for the .wav recording to sound worse in quality than expected. 

The following file types are supported for audio recording output:  
.wav

The following file types are supported for transcription log output:  
.txt .json .srt .vtt

The following CLI options are available:

```options:
  -h, --help            show this help message and exit
  -M, --no_mic          Do not include microphone audio input in recording
  -D, --no_desktop      Do not include desktop audio input in recording
  -r, --set_recording_name SET_RECORDING_NAME
                        Set the desired name of the audio recording output file
                        (default is a.wav supported file types are ['wav'])
  -o, --set_output_name SET_OUTPUT_NAME
                        Set the desired name of the transcription output file (default 
                        is a.txt supported file types are ['txt', 'json', 'srt', 'vtt'])
  -m, --set_mic SET_MIC
                        Set the desired microphone audio device by inputting a string 
                        that will be searched for from the names of your available input
                        devices. input is case insensitive (default is 'Microphone')
  -d, --set_desktop SET_DESKTOP
                        Set the desired desktop audio device by inputting a string that
                        will be searched for from the names of your available input
                        devices, input is case insensitive (default is 'Stereo Mix')
  -mb, --set_mic_backend SET_MIC_BACKEND
                        Set the desired microphone audio backend by inputting a string
                        that will be searched for from the names of your available input
                        devices, input is case insensitive (default is 'Windows WASAPI')
  -md, --set_desktop_backend SET_DESKTOP_BACKEND
                        Set the desired desktop audio backend by inputting a string that
                        will be searched for from the audio backends of your available
                        input devices, input is case insensitive (default is 'Windows
                        WASAPI')
  -s, --set_model_dir SET_MODEL_DIR
                        Set the name of the desired speech recognition model directory to
                        use for transcription. The input will searched from the names of
                        available directories inside the models directory, input is case
                        insensitive (default is 'vosk-model-small-en-us-0.15')```