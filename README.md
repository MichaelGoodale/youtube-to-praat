# youtube-to-praat 

This is a Python 3 script which takes in a link to a YouTube video, or a number of YouTube video links and downloads both the audio and the automatically generated captions for them.
These captions are then used to create a Praat TextGrid of utterances, which is turned forced aligned with the Montreal Forced Aligner.

Currently it only uses the auto-generated subtitles on YouTube videos rather than hand-written subtitles.

## Getting Started

### Installing

In order to run the script you must first run `pip install -r requirements.txt` to install all necessary Python packages.
Additionally, if you intend to use the Montreal Forced Aligner with it, you must change the `MFA_BIN` variable in `download.py` to the path to the directory of `mfa_align` on your system.

### Using the script

The simplest use-case is to download one YouTube video and forced-align it.
```
python3 download.py https://www.youtube.com/watch?v=OmIxrpI8-4M
```

You can also provide multiple videos, or even a link to a playlist(since YouTube playlist links contain an ampersand, make sure that you surround the link in quotes).
```
python3 download.py https://www.youtube.com/watch?v=2MsNyR-epBM "https://www.youtube.com/watch?v=4wetwETy4u0&list=PLA34681B9BE88F5AA"
```

Finally you can also provide a file with a list of youtube links seperated by newlines like so:

```
python3 download.py --file_path youtube_videos.txt
```

You can also include video links as arguments and as a file at the same time.

### Script details
Files are named like so `user_id.video_id.ext`. 
TextGrid tiers use this user as the speaker for the video(since youtube's auto-subtitles don't distinguish between speakers).

If a video does not have automatic captions, the audio file will still be downloaded, but nothing will be done with it.

More options can be accessed by running `python3 download.py -h`

#### Languages other than English

By default, youtube-dl will always download the English subtitles, and if there are none it will auto-translate the subtitles into English, and download this.
In order to circumvent this, if you want to use another language, you must provide the `--language` flag with the two letter code of the language you intend to use(e.g. `en` for English, `fr` for French, and so on).

If you intend to use this with the MFA step, make sure that you also change the pronunciation dictionary and the alignment model as well. 

## Author

* **Michael Goodale** 

## License

This project is licensed under the GPL v3 License - see the [LICENSE.md](LICENSE.md) file for details
