import m3u8
import requests
from youtube_transcript_api import YouTubeTranscriptApi

# for extracting video id ex https://youtu.be/jy05rJqsRB4 --> ['https:', '', 'youtu.be', 'jy05rJqsRB4']
YOUTUBE_URL_INDEX = 3

def unit_testing():
    """
    Unit testing
    """
    # youtube video
    video_url = "https://youtu.be/jy05rJqsRB4"
    print("Youtube video url: {url}".format(url=video_url))
    print("Youtube video subtitles: {subtitles}".format(subtitles=get_subtitles_from_url(video_url=video_url)))

    # wistia video (from m3u8 file)
    video_url = "https://fast.wistia.net/embed/captions/n8em8nhchj.m3u8?language=eng"
    print("Wistia video url: {url}".format(url=video_url))
    print("Wistia video subtitles: {subtitles}".format(subtitles=get_subtitles_from_url(video_url=video_url)))

    # wistia (from vtt file)
    video_url = "https://fast.wistia.net/embed/captions/3ijia54m8c.vtt?language=eng"
    print("Wistia video url: {url}".format(url=video_url))
    print("Wistia video subtitles: {subtitles}".format(subtitles=get_subtitles_from_url(video_url=video_url)))

    # Invalid video url
    try:
        video_url = "testing.com"
        print("Invalid video url: {url}".format(url=video_url))
        print("Invalid video subtitles: {subtitles}".format(subtitles=get_subtitles_from_url(video_url=video_url)))
    except Exception as e:
        print("Invalid video url exception: {exception}".format(exception=e))

def get_subtitles_from_url(video_url=""):
    """
    Get subtitles from video url
    Throws an exception if url is invalid
    """
    if "https://youtu.be/" not in video_url and "wistia" not in video_url:
        raise Exception("Invalid video url, must be in the format: https://youtu.be/VIDEO_ID or https://fast.wistia.net/embed/captions/VIDEO_ID.m3u8?language=eng")
    
    if "https://youtu.be/" in video_url:
        return get_subtitles_from_youtube(video_url)
    return get_subtitles_from_wistia(video_url)

def get_subtitles_from_youtube(video_url=""):
    """
    Get subtitles from youtube video url
    Throws an exception if url is invalid
    """
    if "https://youtu.be/" not in video_url:
        raise Exception("Invalid youtube video url, must be in the format: https://youtu.be/VIDEO_ID")

    # extract video id
    video_id = video_url.split("/")
    video_id = video_id[YOUTUBE_URL_INDEX]

    # Get list of available transcripts and get english transcript
    transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
    transcript = transcript_list.find_transcript(["en"])
    transcript_json = transcript.fetch()

    text = ""
    for subtitle in transcript_json:
        text += "{subtitle} ".format(subtitle=subtitle["text"])
    return text

def get_subtitles_url(video_url=""):
    """
    Get subtitles url from m3u8 file
    For use with get_subtitles_from_wistia
    """
    playlist = m3u8.load(video_url)
    subtitles_url = playlist.__dict__["data"]["segments"][0]["uri"]
    return subtitles_url

def get_subtitles_from_subtitles_file(subtitles_file=""):
    """
    Get subtitles from subtitles file
    For use with get_subtitles_from_wistia
    """
    text = ""
    for subtitle in subtitles_file:
        if subtitle.isdigit() or "-->" in subtitle or subtitle in "\n":
            continue
        text += "{subtitle} ".format(subtitle=subtitle)
    text = text.replace("WEBVTT", "")
    return text

def get_subtitles_from_wistia(wistia_url=""):
    """
    Get subtitles from wistia video url
    Throws an exception if no subtitles are found
    """
    if "captions" not in wistia_url and "m3u8" not in wistia_url and "vtt" not in wistia_url:
        raise Exception("No captions found in the video url")

    subtitles_url = ""
    if "m3u8" in wistia_url:
        subtitles_url = get_subtitles_url(video_url=wistia_url)
    elif "vtt" in wistia_url:
        subtitles_url = wistia_url
    else:
        raise Exception("No subtitles url found")
    
    response = requests.get(subtitles_url)
    subtitles_file = response.__dict__["_content"].decode("utf-8")
    subtitles_file = subtitles_file.splitlines()

    return get_subtitles_from_subtitles_file(subtitles_file=subtitles_file)

if __name__ == "__main__":
    unit_testing()