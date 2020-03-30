import time
import board
import busio
import digitalio
import storage
import os
import displayio
from adafruit_bitmap_font import bitmap_font
import adafruit_sdcard
import audioio
from adafruit_pyportal import PyPortal
from adafruit_button import Button

# to read docs for PyPortal:
# https://github.com/adafruit/Adafruit_CircuitPython_PyPortal/blob/master/adafruit_pyportal.py#L255

#### Global Variables ###
is_paused = False
music_file_name = ""
music_wav_file = ""


# Set up where we'll be fetching data from
#DATA_SOURCE = "https://www.adafruit.com/api/quotes.php"
#QUOTE_LOCATION = [0, 'text']
#AUTHOR_LOCATION = [0, 'author']

# the current working directory (where this file is)
# the current working directory (where this file is)
cwd = ("/"+__file__).rsplit('/', 1)[0]
'''
pyportal = PyPortal(url= None,
                    json_path = None,
                    status_neopixel=board.NEOPIXEL,
                    default_bg=cwd+"/quote_background.bmp",
                    text_font=cwd+"/fonts/Arial-ItalicMT-17.bdf",
                    text_position=((20, 120),  # quote location
                                   (5, 210)), # author location
                    text_color=(0xFFFFFF,  # quote text color
                                0x8080FF), # author text color
                    text_wrap=(35, # characters to wrap for quote
                               0), # no wrap for author
                    text_maxlen=(180, 30), # max text size for quote & author
                   )
'''
BACKGROUND_COLOR = 0x443355
pyportal = PyPortal(default_bg=BACKGROUND_COLOR)

# speed up projects with lots of text by preloading the font!
# pyportal.preload_font()

# Default location to look is in internal memory
MUSIC_DIRECTORY = "/sd/music"

# Enable the speaker
# Info on speaker, audio, playing wav file
# Appears to be handled automatically by the pyportal object
# https://learn.adafruit.com/adafruit-circuit-playground-express/circuitpython-audio-out
'''
speaker_enable = digitalio.DigitalInOut(board.SPEAKER_ENABLE)
speaker_enable.direction = digitalio.Direction.OUTPUT
speaker_enable.value = True
'''

def play_file(filename):
    print("Playing file: " + filename)
    wave_file = open(filename, "rb")
    with audioio.WaveFile(wave_file) as wave:
        with audioio.AudioOut(board.A0) as audio:
            audio.play(wave)
            while audio.playing:
                pass
    print("Finished")

def print_directory(path, tabs=0):
    for file in os.listdir(path):
        stats = os.stat(path + "/" + file)
        filesize = stats[6]
        isdir = stats[0] & 0x4000

        if filesize < 1000:
            sizestr = str(filesize) + " by"
        elif filesize < 1000000:
            sizestr = "%0.1f KB" % (filesize / 1000)
        else:
            sizestr = "%0.1f MB" % (filesize / 1000000)

        prettyprintname = ""
        for _ in range(tabs):
            prettyprintname += "   "
        prettyprintname += file
        if isdir:
            prettyprintname += "/"
        print('{0:<20} Size: {1:>6}'.format(prettyprintname, sizestr))

        # recursively print directory contents
        if isdir:
            print_directory(path + "/" + file, tabs + 1)

try:
    print_directory(MUSIC_DIRECTORY)
except OSError as error:
    raise Exception("No images found on flash or SD Card")

music_file = 'bad_to_the_bone.wav'

def stop_file(pyportal, wavfile):
    wavfile.close()
    pyportal._speaker_enable.value = False
    print("Stopped file = " + str(wavfile))
    return

def play_audio(pyportal, wavfile):
    wavedata = audioio.WaveFile(wavfile)
    board.DISPLAY.wait_for_frame()
    pyportal._speaker_enable.value = True
    pyportal.audio.play(wavedata)
    return

def my_play_audio(pyportal, passed_file_name):
    print("Entering my_play_audio")
    # Global variables:
    # music_file_name = ""
    # music_wav_file = ""
    # is_playing = False
    #
    # Case #1:
    #   - First song played, so music_file_name = ""
    #   - set music_file_name = passed_file_name
    #   - set music_wav_file = get_wavfile(passed_file_name)
    #   - Call play_audio(pyportal, music_wav_file)
    #   - is_playing = True
    # Case #2:
    #   - Different song selected, so passed_file_name != music_file_name
    #   - Stop current song with stop_file(pyportal, music_wav_file)
    #   - set global music_file_name = passed_file_name
    #   - set global music_wav_file = get_wavfile(passed_file_name)
    #   - call play_audio(pyportal, music_wav_file)
    #   - is_playing = True
    # Case #3:
    #   - Same song, so passed_file_name == music_file_name
    #   - Hit pause / play button, so passed_file_name == music_file_name
    #   - if is_playing == False:
    #      * unpause_audio(pyportal)
    #      * is_playing = True
    #   - if is_playing == True:
    #      * pause_audio(pyportal)
    #      * is_playing = False
    #
    global music_file_name
    global music_wav_file
    global is_playing

    if music_file_name == "":
        print("First time a song played since reboot")
        music_file_name = passed_file_name
        music_wav_file = get_wavfile(passed_file_name)
        is_playing = True
        play_audio(pyportal, music_wav_file)
    elif music_file_name != passed_file_name:
        print("New song selected")
    elif music_file_name == passed_file_name:
        print("Need to pause or unpause song")
        if is_playing == False:
            print("Resume song")
            #unpause_audio(pyportal)
            pyportal.audio.resume()
            is_playing = True
        elif is_playing == True:
            print("Paused song")
            #pause_audio(pyportal)
            pyportal.audio.pause()
            is_playing = False

def get_wavfile(file_name):
    wavfile = open(file_name, "rb")
    return wavfile


######################
# Create buttons
######################
the_font = '/fonts/Arial-ItalicMT-17.bdf'
font = bitmap_font.load_font(the_font)
buttons = []
button = Button(x=10, y=10, width=120, height=60,
                style=Button.SHADOWROUNDRECT,
                fill_color=(255, 0, 0),
                outline_color=0x222222,
                name='/sd/music/bad_to_the_bone.wav',
                label_font = font,
                label='Bad to the Bone',
                )
pyportal.splash.append(button.group)
buttons.append(button)
# Next button

wavfile = get_wavfile('/sd/music/bad_to_the_bone.wav')
#play_audio(pyportal, wavfile)

while True:
    touched = pyportal.touchscreen.touch_point
    # Returns tuple of (X,Y,?)
    # X range 0...320
    # Y range 0...240
    if touched:
        for button in buttons:
            if button.contains(touched):
                print("Touched", button.name)
                print("file", button.name)
                # Call play_audio(pyportal, filename)
                #play_audio(pyportal,get_wavfile(button.name))
                my_play_audio(pyportal, button.name)


        time.sleep(0.3)