import os
import sys
import subprocess 
import shutil
import argparse

import webvtt
import youtube_dl
import textgrid


MFA_BIN = "/home/michael/Documents/montreal-forced-aligner/bin"


parser = argparse.ArgumentParser(description="does stuff")
parser.add_argument("videos", nargs="*",
        help="YouTube videos to download")
parser.add_argument("--file_path", default=None,
        help="File with YouTube videos to download(separated by newlines)")
parser.add_argument("--language", default="en",
        help="Two letter language code of video subtitles")

parser.add_argument('-skip_mfa', action='store_true',
        help="Skip forced alignment with MFA")
parser.add_argument('--mfa_model', default='english',
        help="Path to model for MFA, by default the pretrained English model")
parser.add_argument('--mfa_dict', default='librispeech.txt',
        help="Path to pronunciation dictionary")

parser.add_argument("--output_dir", default="aligned_textgrids", 
        help="The directory for the final forced-aligned WAVs and TextGrids")
parser.add_argument("--utterance_output_dir", default="textgrids", 
        help="The directory for the TextGrids with subtitles as utterances")
parser.add_argument("--temp_dir", default="temp", 
        help="The directory to download the original subtitle files")

args = parser.parse_args()

ALIGNED_DIR = args.output_dir
TEMP_DIR = args.temp_dir
TEXTGRID_DIR = args.utterance_output_dir

os.makedirs(TEMP_DIR, exist_ok=True)
os.makedirs(TEXTGRID_DIR, exist_ok=True)
if not args.skip_mfa:
    os.makedirs(ALIGNED_DIR, exist_ok=True)

if args.videos == [] and args.file_path is None:
    print("At least one link to a video must be provided")
    sys.exit(1)

youtube_videos = args.videos

if args.file_path is not None:
    with open(args.file_path, "r") as f:
        for l in f:
            youtube_videos.append(l.strip())

language = str(args.language).lower()

YDL_OPTS = {
    'format': 'bestaudio/best',
    'writeautomaticsub': True,
    'outtmpl': TEMP_DIR+'/%(uploader_id)s.%(id)s.%(ext)s',
    'subtitleslangs':[language],
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'wav',
    }]
}

with youtube_dl.YoutubeDL(YDL_OPTS) as ydl:
    ydl.download(youtube_videos)

file_ending = ".{}.vtt".format(language)
subtitle_files = list(filter(lambda x: x.endswith(file_ending), os.listdir(TEMP_DIR)))
for subtitle in subtitle_files:
    #Check there's an audio file associated
    audio = subtitle.replace(file_ending, ".wav")
    if not os.path.isfile(os.path.join(TEMP_DIR, audio)):
        print("Audio file {} is missing".format(audio))
        continue

    speaker = subtitle.split(".")[0] 
    #Make sure the subtitles don't overlap as there are overlapping subtitles 
    #in youtube's auto-generated subs
    captions = webvtt.read(os.path.join(TEMP_DIR, subtitle)).captions


    #Even captions have the time of the utterance (as well as the time of the individual words)
    #Odd captions have the actual utterance string
    tier = textgrid.IntervalTier(speaker)
    for cap_time, cap_string in zip(captions[::2], captions[1::2]):
        tier.add(cap_time.start_in_seconds, cap_time.end_in_seconds, \
                cap_string.text.strip())

    tg = textgrid.TextGrid()
    tg.append(tier)
    tg.write(os.path.join(TEXTGRID_DIR, subtitle.replace(file_ending, ".TextGrid")))
    shutil.move(os.path.join(TEMP_DIR, audio), \
                os.path.join(TEXTGRID_DIR, audio))
if not args.skip_mfa:
    subprocess.run([os.path.join(MFA_BIN, "mfa_align"), TEXTGRID_DIR, \
            args.mfa_dict, args.mfa_model, ALIGNED_DIR, "--verbose"])

    for subtitle in subtitle_files:
        audio = subtitle.replace(file_ending, ".wav")
        if not os.path.isfile(os.path.join(TEXTGRID_DIR, audio)):
            continue
        shutil.move(os.path.join(TEXTGRID_DIR, audio), os.path.join(ALIGNED_DIR, audio))
