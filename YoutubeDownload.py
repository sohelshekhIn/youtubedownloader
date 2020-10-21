
from pytube import YouTube
import requests

class YoutubeVideo():
    def __init__(self, url):
        self.url = url
        self.Video = YouTube(url)
        self.streams = self.Video.streams

    def convert_bytes(self, size):
        """
        Returns size in KB/MD ...
        Takes 1 argument:
            size -int: Bytes
        """
        for i in ['bytes', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return "%3.1f %s" % (size, i)
            size /= 1024.0

        return size

    def removeDuplicateStreams(self, streams):
        videoStreamQuality = []
        videoStreamPosition = []
        videoNewStreams = []
        audioStreamSize = []
        audioStreamPosition = []
        newAudioStream = []
        
        for i in range(len(streams)):
            if "video" in str(streams[i][3]):
                if not "None" in str(streams[i][1]):
                   if not "webm" in str(streams[i][3]):
                    if not streams[i][1] in videoStreamQuality:
                        videoStreamQuality.append(streams[i][1])
                        videoStreamPosition.append(i)
            elif "audio" in str(streams[i][3]):
                if not streams[i][2] in audioStreamSize:
                    audioStreamSize.append(streams[i][2])
                    audioStreamPosition.append(i)
                
        for i in range(len(videoStreamPosition)):
            videoNewStreams.append(streams[videoStreamPosition[i]])
            videoNewStreams.sort(key=lambda tup: tup[1])
            
        for i in range(len(audioStreamPosition)):
            audioStream = streams[audioStreamPosition[i]]
            if str(audioStream[1]) == "None":
                lst = list(audioStream)
                lst[1] = "Audio"
                audioStream = tuple(lst)
            newAudioStream.append(audioStream)
        return videoNewStreams + newAudioStream


    def get_streams(self):
        """
        Returns array of streams with 
        stream_id, stream_resolution, stream_filesize, stream_mime_type
        """
        newStream = []
        for i in range(len(self.streams)):
            # if not "/webm" in str(self.streams[i].mime_type):
            listStream = (i ,self.streams[i].resolution, self.convert_bytes(self.streams[i].filesize_approx), self.streams[i].mime_type)
            newStream.append(listStream)
        return self.removeDuplicateStreams(newStream)

    def download(self, stream_id, file_path = None):
        """
        Dowloads the video:
        Takes 2 arguments:
            stream_id - int: id of stream (found in get_streams())
            file_path - str: (Optional) Path where file is to be downloaded, default is working dir!
        """
        stream_id = self.get_streams()[0][0]
        self.Video.streams[stream_id].download(file_path)

    def get_details(self):
        """
        Returns details in tuple
        (thumbnailUrl, title, authorName, url) 
        """
        title = self.Video.title
        authorName = self.Video.author
        thumbnailUrl = self.Video.thumbnail_url
        return (thumbnailUrl, title, authorName, self.url)

    def download_progress(self, func):
        """
        Rreturns functional arguments:
        chunk which also conatain filesize
        filehandle, file_size
        """
        self.Video.register_on_progress_callback(func)
    
    def download_complete(self, func):
        """
        Return functional argument:
        filepath;
        """
        self.Video.register_on_complete_callback(func)

if __name__ == "__main__":
    url = "https://youtu.be/6kwrsQLQnhA"
    yt = YoutubeVideo(url)
    print(yt.get_details())
    print(yt.get_streams)
    # yt.download(2)
    
    
    
    
    
"""
[
<Stream: itag="18" mime_type="video/mp4" res="360p" fps="30fps" vcodec="avc1.42001E" acodec="mp4a.40.2" progressive="True" type="video">,
<Stream: itag="244" mime_type="video/webm" res="480p" fps="30fps" vcodec="vp9" progressive="False" type="video">,
<Stream: itag="397" mime_type="video/mp4" res="None" fps="30fps" vcodec="av01.0.04M.08.0.110.05.01.06.0" progressive="False" type="video">,
<Stream: itag="135" mime_type="video/mp4" res="480p" fps="30fps" vcodec="avc1.4d401e" progressive="False" type="video">,
<Stream: itag="243" mime_type="video/webm" res="360p" fps="30fps" vcodec="vp9" progressive="False" type="video">,
<Stream: itag="396" mime_type="video/mp4" res="None" fps="30fps" vcodec="av01.0.01M.08.0.110.05.01.06.0" progressive="False" type="video">,
<Stream: itag="134" mime_type="video/mp4" res="360p" fps="30fps" vcodec="avc1.4d4015" progressive="False" type="video">,
<Stream: itag="242" mime_type="video/webm" res="240p" fps="30fps" vcodec="vp9" progressive="False" type="video">,
<Stream: itag="395" mime_type="video/mp4" res="None" fps="30fps" vcodec="av01.0.00M.08.0.110.05.01.06.0" progressive="False" type="video">,
<Stream: itag="133" mime_type="video/mp4" res="240p" fps="30fps" vcodec="avc1.4d400c" progressive="False" type="video">,
<Stream: itag="278" mime_type="video/webm" res="144p" fps="30fps" vcodec="vp9" progressive="False" type="video">,
<Stream: itag="394" mime_type="video/mp4" res="None" fps="30fps" vcodec="av01.0.00M.08.0.110.05.01.06.0" progressive="False" type="video">,
<Stream: itag="160" mime_type="video/mp4" res="144p" fps="30fps" vcodec="avc1.4d400b" progressive="False" type="video">,
<Stream: itag="140" mime_type="audio/mp4" abr="128kbps" acodec="mp4a.40.2" progressive="False" type="audio">,
<Stream: itag="249" mime_type="audio/webm" abr="50kbps" acodec="opus" progressive="False" type="audio">,
<Stream: itag="250" mime_type="audio/webm" abr="70kbps" acodec="opus" progressive="False" type="audio">, 
<Stream: itag="251" mime_type="audio/webm" abr="160kbps" acodec="opus" progressive="False" type="audio">
]
"""