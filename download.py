import os
import subprocess 
import shutil
import argparse

import webvtt
import youtube_dl
import textgrid

BAD_STUFF = ["\n"]
def strip_bad_stuff(s):
    for x in BAD_STUFF:
        s = s.replace(x, '')
    return s.upper()

TEMP_DIR = "output"
TEXTGRID_DIR = "textgrids"
ALIGNED_DIR = "aligned_textgrids"
LANGUAGES = ["en"]

PRON_DICT = "librispeech.txt"
MFA_BIN = "/home/michael/Documents/montreal-forced-aligner/bin"

YDL_OPTS = {
    'format': 'bestaudio/best',
    'writeautomaticsub': True,
    'outtmpl': TEMP_DIR+'/%(uploader_id)s.%(id)s.%(ext)s',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'wav',
    }]
}


parser = argparse.ArgumentParser(description="does stuff")
parser.add_argument("videos", nargs="+",
        help="YouTube videos to download")
args = parser.parse_args()
youtube_videos = args.videos

with youtube_dl.YoutubeDL(YDL_OPTS) as ydl:
    ydl.download(youtube_videos)

for subtitle in filter(lambda x: x.endswith(".vtt"), os.listdir(TEMP_DIR)):
    #Guess what language the file is
    for l in LANGUAGES:
        if subtitle.endswith(".{}.vtt".format(l)):
            language = l
            file_ending = ".{}.vtt".format(language)
            break

    #Check there's an audio file associated
    audio = subtitle.replace(file_ending, ".wav")
    if not os.path.isfile(os.path.join(TEMP_DIR, audio)):
        print("Audio file {} is missing".format(audio))

    speaker = subtitle.split(".")[0] 
    #Make sure the subtitles don't overlap as there are overlapping subtitles 
    #in youtube's auto-generated subs
    captions = webvtt.read(os.path.join(TEMP_DIR, subtitle)).captions


    #Even captions have the time of the utterance (as well as the time of the individual words)
    #Odd captions have the actual utterance string
    tier = textgrid.IntervalTier(speaker)
    for cap_time, cap_string in zip(captions[::2], captions[1::2]):
        tier.add(cap_time.start_in_seconds, cap_time.end_in_seconds, \
                strip_bad_stuff(cap_string.text))

    tg = textgrid.TextGrid()
    tg.append(tier)
    tg.write(os.path.join(TEXTGRID_DIR, subtitle.replace(file_ending, ".TextGrid")))
    shutil.move(os.path.join(TEMP_DIR, audio), \
                os.path.join(TEXTGRID_DIR, audio))
    

subprocess.run([os.path.join(MFA_BIN, "mfa_align"), TEXTGRID_DIR, \
        PRON_DICT, "english", ALIGNED_DIR, "--verbose"])

