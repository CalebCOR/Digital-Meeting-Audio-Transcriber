# Digital-Meeting-Audio-Transcriber
By Caleb Corlett, Version 1.0.0 (7-31-2025)

A Python script to transcribe desktop audio and microphone input to a time-stamped .txt log and also produce a .wav file of the transcribed audio.

To Run:
1) Make sure the latest version of Python 3 is installed.
2) Install the necessary requirements with `pip install -r requirements.txt` or `python -m pip install -r requirements.txt`.
3) Run `python desktop_audio_transcriber.py` to begin a new recording.

3.5) The desktop_audio_transcriber.py file has a list of constant variables (lines **11-23**) that can be modified to more appropriately fit your needs. This will likely be required on anything other than Windows.

:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

Vosk Offline Speech Recognition models are used to transcribe the audio to text. The small en-us model (300mb vram required) is included by default. More advanced models can be downloaded from `https://alphacephei.com/vosk/models`. Once downloaded, place the model directory into the \models directory and update the `MODEL_DIRECTORY` variable on line **16** of desktop_audio_transcriber.py with the new model directory name.

The .txt log produced contains the transcribed audio along with timestamps for both the actual time the words were said (ex. a word said at 1:45pm can be found at the 13:45:00 timestamp) as well as the relative time where the words can be found in the recording (ex. a word said 1 hour, 15 minutes, and 30 seconds into the .wav recording can found at the 01:15:30 timestamp)

timestamps are placed in the .txt log every 10 seconds by default, can be modified by changing the `TRANSCRIPTION_TIMESTAMP_FREQUENCY` variable on line **23** of desktop_audio_transcriber.py.

The .wav recording is downsampled to 16khz sample rate for better use with the transcriber. It is normal for the .wav recording to sound worse in quality than expected. 
