import os

import webvtt
import youtube_dl
import textgrid


def strip_bad_stuff(caption): 
    caption.text = caption.text.replace("\n", "")
    return caption

TEMP_DIR = "output"
TEXTGRID_DIR = "textgrids"
ALIGNED_DIR = "aligned_textgrids"


LANGUAGES = ["en"]

ydl_opts = {
    'format': 'bestaudio/best',
    'writeautomaticsub': True,
    'outtmpl': TEMP_DIR+'/%(id)s.%(ext)s',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }]
}

#with youtube_dl.YoutubeDL(ydl_opts) as ydl:
#    ydl.download(['https://www.youtube.com/watch?v=BaW_jenozKc'])

for subtitle in filter(lambda x: x.endswith(".vtt"), os.listdir(TEMP_DIR)):
    
    found_file = False
    for l in LANGUAGES:
        audio = subtitle.replace(".{}.vtt".format(l), ".mp3")
        if os.path.isfile(os.path.join(TEMP_DIR, audio)):
            found_file = True
            break

    if not found_file:
        print("Audio file {} is missing".format(audio))
    
    non_overlapping_captions = []
    for cap in webvtt.read(os.path.join(TEMP_DIR, subtitle)):
        if len(non_overlapping_captions) == 0 or non_overlapping_captions[-1].end <= cap.start:
            non_overlapping_captions.append(strip_bad_stuff(cap))

    tier = textgrid.IntervalTier("words")
    for cap in non_overlapping_captions:
        tier.add(cap.start_in_seconds, cap.end_in_seconds, cap.text)


