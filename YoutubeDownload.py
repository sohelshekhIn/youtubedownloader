# from flask import app
from pytube import YouTube


class YoutubeVideo:
    def __init__(self, url):
        """Youtube Class that allows to get details of the video, available streams of video, download video and many more"""
        self.url = url
        self.Video = YouTube(url)
        self.streams = self.Video.streams

    def convert_bytes(self, size):
        """
        Returns size in KB/MD ...
        Takes 1 argument:
            size -int: Bytes
        """
        for i in ["bytes", "KB", "MB", "GB", "TB"]:
            if size < 1024.0:
                return "%3.1f %s" % (size, i)
            size /= 1024.0

        return size

    def addAudioSize(self, videoFileSize) -> int:
        """Adds the size of audio to videos which are not progressive (does not contain audio)

        Args:
            videoFileSize (byte): Takes video file size as bytes

        Returns:
            totalSize: Returns an int of calculated size
        """
        audioFile = self.streams.filter(only_audio=True).first()
        audioSize = audioFile.filesize or audioFile.filesize_approx
        totalSize = int(videoFileSize) + int(audioSize)
        return int(totalSize)

    def removeDuplicates(self, videoStreams, progressiveStreams) -> list:
        """Removes duplicate video streams that are already present in progressive Streams

        Args:
            videoStreams (ListObject): List of video streams
            progressiveStreams (ListObject): List of progressive streams

        Returns:
            videoStreams: Returns new sorted list of video streams
        """
        sortedVideoStreams = []
        for i in range(len(progressiveStreams)):
            for j in range(len(videoStreams)):
                if str(videoStreams[j][1]) != "None":
                    if not str(progressiveStreams[i][1]) == str(videoStreams[j][1]):
                        sortedVideoStreams.append(videoStreams[j])

        sortedVideoStreams = [t for t in (set(tuple(i) for i in sortedVideoStreams))]
        sortedVideoStreams.sort(key=lambda x: x[1])
        return sortedVideoStreams

    def get_origianl_streams(self):
        """ "
        Returns list of original streams directly from pytube
        """
        return self.streams

    def is_progressive(self, stremid) -> bool:
        """Checks whether the stream with itag stream id is a progressive stream or not!

        Args:
            stremid (int): itag of stream

        Returns:
            bool: Returns True or False according to situation
        """
        return self.streams.get_by_itag(int(stremid)).is_progressive

    def get_streams(self):
        """
        Returns array of streams with
        stream_id, stream_resolution, stream_filesize, stream_mime_type
        """
        userStreams = []
        audioStreams = self.streams.filter(only_audio=True)
        videoStreams = self.streams.filter(
            subtype="mp4", adaptive=True, only_video=True
        )
        progressiveStreams = self.streams.filter(progressive="True")
        audioStreamsFormatted = []
        videoStreamsFormatted = []
        progressiveStreamsFormatted = []
        audioToJoin = []

        for i in range(len(audioStreams)):
            audioStream = (
                audioStreams[i].itag,
                audioStreams[i].abr,
                self.convert_bytes(
                    audioStreams[i].filesize or videoStreams[i].filesize_approx
                ),
                audioStreams[i].type,
            )
            audioStreamsFormatted.append(audioStream)

        for i in range(len(progressiveStreams)):
            progressiveStream = (
                progressiveStreams[i].itag,
                progressiveStreams[i].resolution,
                self.convert_bytes(
                    progressiveStreams[i].filesize
                    or progressiveStreams[i].filesize_approx
                ),
                progressiveStreams[i].type,
            )
            progressiveStreamsFormatted.append(progressiveStream)

        audioStreamsFormatted.sort(key=lambda x: x[1])
        progressiveStreamsFormatted.sort(key=lambda x: x[1])

        if len(progressiveStreams) < 4 and len(videoStreams) > 4:
            for i in range(len(videoStreams)):
                videoStream = (
                    videoStreams[i].itag,
                    videoStreams[i].resolution,
                    self.convert_bytes(
                        self.addAudioSize(
                            videoStreams[i].filesize or videoStreams[i].filesize_approx
                        )
                    ),
                    videoStreams[i].type,
                )
                videoStreamsFormatted.append(videoStream)
                audioToJoin.append(videoStreams[i].itag)

            videoStreamsFormatted = self.removeDuplicates(
                videoStreamsFormatted, progressiveStreamsFormatted
            )
            userStreams = (
                videoStreamsFormatted
                + progressiveStreamsFormatted
                + audioStreamsFormatted
            )
        elif len(progressiveStreams) > 4 and len(videoStreams) < 4:
            userStreams = progressiveStreamsFormatted + audioStreamsFormatted
        return (userStreams, audioToJoin)

    def download(self, stream_id, file_path=None):
        """
        Dowloads the video:
        Takes 2 arguments:
            stream_id - int: id of stream (found in get_streams())
            file_path - str: (Optional) Path where file is to be downloaded, default is working dir!
        """
        self.streams.get_by_itag(stream_id).download(file_path)

    def downloadAudio(self, filepath):
        """
        Downloads Audio File of the Video
        """
        self.Video.streams.filter(only_audio=True).first().download(filepath)

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
    url = "https://www.youtube.com/watch?v=GwgXoPBt0dM"
    url = "https://www.youtube.com/watch?v=-d9nvq3402M"
    yt = YoutubeVideo(url)
    # print(yt.get_origianl_streams())
    print(yt.get_details())
    print(yt.get_streams())
    # yt.download(2)


"""
For Reference
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
