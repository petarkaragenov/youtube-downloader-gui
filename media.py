from pytube import YouTube
import moviepy.editor as mp
import re
import os

class Media():
    def __init__(self, link, folder):
        self.video = YouTube(link)
        self.folder = folder

    def download_video(self, res):
        filename = self.filename()

        self.video.streams \
            .filter(file_extension="mp4", res=res).first().download(filename=filename) # add res=res to filter


    def filename(self):
        return re.sub(r"[:\W]+", "_", self.video.title) + ".mp4"


    def download_audio(self):
        filename = self.filename()

        streams = self.video.streams \
            .filter(only_audio=True) \
            .first() \
            .download(filename=filename)

        return filename


    def get_resolutions(self):
        streams = self.video.streams \
                    .filter(file_extension="mp4") \
                    .order_by('resolution') \
                    .desc()

        avail_res = list()

        for stream in streams:
            qual = re.search(r'res="([0-9]{3,4}p)"', stream.__repr__()).group(1)
            if qual not in avail_res: 
                avail_res.append(qual)  

        return avail_res    


    def convert_to_audio(self, filename):
        initial_format = mp.AudioFileClip(filename)
        initial_format.write_audiofile(f"{filename.split('.')[0]}.mp3")
        os.remove(filename)

    def move_to_folder(self):
        for file in os.listdir():
            if file == "__pycache__":
                pass
            else:
                ext = file.split(".")[1]
                if ext in ("mp3", "mp4"):               
                    original_path = os.path.join(os.path.dirname(os.path.realpath(file)), file)
                    os.rename(original_path, f"{self.folder}/{file}")
