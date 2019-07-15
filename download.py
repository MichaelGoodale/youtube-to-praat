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
YDL_OPTS = {
    'format': 'bestaudio/best',
    'writeautomaticsub': True,
    'outtmpl': TEMP_DIR+'/%(id)s.%(ext)s',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }]
}

youtube_videos = ['https://www.youtube.com/watch?v=BaW_jenozKc']

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
    audio = subtitle.replace(file_ending, ".mp3")
    if not os.path.isfile(os.path.join(TEMP_DIR, audio)):
        print("Audio file {} is missing".format(audio))

    #Make sure the subtitles don't overlap as there are overlapping subtitles 
    #in youtube's auto-generated subs
    non_overlapping_captions = []
    for cap in webvtt.read(os.path.join(TEMP_DIR, subtitle)):
        if len(non_overlapping_captions) == 0 or non_overlapping_captions[-1].end <= cap.start:
            non_overlapping_captions.append(strip_bad_stuff(cap))


    #Create a textgrid with intervals of the subtitles
    tier = textgrid.IntervalTier("words")
    for cap in non_overlapping_captions:
        tier.add(cap.start_in_seconds, cap.end_in_seconds, cap.text)

    tg = textgrid.TextGrid()
    tg.append(tier)
    tg.write(os.path.join(TEXTGRID_DIR, subtitle.replace(file_ending, ".TextGrid")))
