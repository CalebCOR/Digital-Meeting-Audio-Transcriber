# pylint: disable=line-too-long
""" Python Script to convert a timestamp and associated string into a log for a txt, json, srt, or vtt file """
# To add output support to a new file type, write a function with the 
# following parameters, then add the filetype and the function name 
# into type_outputs dict at the bottom of this file.:
#      
#       p_file_pointer: An open file object (file pointer)
#       p_timestamp: The timestamp for the transcribed text (datetime.datetime)
#       p_rel_timestamp: The timestamp to write (timestamp (from python's datetime module))
#       p_duration: The duration (in seconds) of the transcription window (int)
#       p_text: The text to write (string)
#       header_string: A string of header information to write on first write to the file
#       footer_string: A string of footer information to write on final write to the file
#
#       static_count can be used if you need an incrementing count included in your writes.
#       
# You can implement behavior for only the first write and final write by checking if
# p_header_string or p_footer_string are anything other than False
#

import json
import datetime

static_count = 0


def to_txt(p_file_pointer, p_timestamp, p_rel_timestamp, p_duration, p_text_string, *, header_string = False, footer_string = False):
    """ Convert a timestamp and associated string into a log for a txt file """

    if header_string:
        p_file_pointer.write(header_string + "\n------------------------------------------------------\n")

    if footer_string:
        return

    timestamp_string = f"\n{p_timestamp.strftime("%H:%M:%S")}, {p_rel_timestamp.strftime("%H:%M:%S")} - "
    p_file_pointer.write(timestamp_string)
    p_file_pointer.write(p_text_string)


def to_json(p_file_pointer, p_timestamp, p_rel_timestamp, p_duration, p_text_string, *, header_string = False, footer_string = False):
    """ Convert a timestamp and associated string into a log for a json file """

    if header_string:
        p_file_pointer.write('[\n')
        split_header = header_string.split(' ')
        audio_file_name = split_header[2][:-1]
        creation_timestamp = f'{split_header [-2]} {split_header [-1][:-1]}'
        json.dump({\
            'audio_file_name':audio_file_name, \
            'creation_timestamp':creation_timestamp}, \
            p_file_pointer)

    elif footer_string:
        p_file_pointer.write('\n]')
        return
    
    p_file_pointer.write(',\n')
    json.dump({\
        'time_stamp':p_timestamp.strftime("%D %H:%M:%S"), \
        'rel_timestamp':p_rel_timestamp.strftime("%H:%M:%S"), \
        'duration':p_duration, \
        'text':p_text_string}, \
        p_file_pointer, indent=4)
    


def to_srt(p_file_pointer, p_timestamp, p_rel_timestamp, p_duration, p_text_string, *, header_string = False, footer_string = False):
    """ Convert a timestamp and associated string into a log for a srt file """

    global static_count

    static_count += 1

    if header_string:
        p_file_pointer.write("\n\n")

    elif footer_string:
        return

    p_file_pointer.write(f"{str(static_count)}\n")
    end_timestamp = p_rel_timestamp + datetime.timedelta(seconds=p_duration)
    p_file_pointer.write(f"{p_rel_timestamp.strftime("%H:%M:%S")},000 --> {end_timestamp.strftime("%H:%M:%S")},000\n")
    p_file_pointer.write(f"{p_text_string}")
    


def to_vtt(p_file_pointer, p_timestamp, p_rel_timestamp, p_duration, p_text_string, *, header_string = False, footer_string = False):
    """ Convert a timestamp and associated string into a log for a vtt file """

    global static_count

    static_count += 1

    if header_string:
        p_file_pointer.write(f"WEBVTT - {header_string}")

    elif footer_string:
        return

    p_file_pointer.write("\n\n")
    end_timestamp = p_rel_timestamp + datetime.timedelta(seconds=p_duration)
    p_file_pointer.write(f"{p_rel_timestamp.strftime("%H:%M:%S")}.000 --> {end_timestamp.strftime("%H:%M:%S")}.000\n")
    p_file_pointer.write(f"{p_text_string}")


# Link file types to output functions here
type_outputs = {'txt':to_txt, 'json':to_json, 'srt':to_srt, 'vtt':to_vtt}
