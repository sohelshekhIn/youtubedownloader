from flask import Flask, request, render_template, send_from_directory, Response, redirect, flash
from YoutubeDownload import YoutubeVideo
from threading import Timer
from werkzeug.utils import secure_filename
import os
import sys, subprocess

# Flask App Initialize
app = Flask("__name__")

#App Configurations
app.secret_key = 'YT$#ek#@@!@$0#el'

# Global variables
yt = ""
url = ""
streams = ""
download_file_name = ""

# req vars
isAudio = False
delay_in_secs = 5
downloadStatus = False
is_notProgressive = False
audioFilePath = ""

YOUTUBE_FILES = "YouTube_Files"
AUDIO_FILES = "Audio_Dir"


# Remove the downloaded file from the directory
def removeFile(path,fileName):
    if str(path) == "False":
        os.remove(os.path.join(YOUTUBE_FILES, fileName))
    else:
        os.remove(os.path.join(path, fileName))

# Download Status to True for redirection and run remove file function
def redirectUser(stream, filepath):
    global downloadStatus, download_file_name, isAudio, is_notProgressive, audioFilePath
    downloadStatus = True
    oldFilePath = filepath
    fileName = os.path.basename(filepath)
    fileName = secure_filename(fileName)
    filepath = os.path.join(YOUTUBE_FILES, fileName)
    os.rename(oldFilePath, filepath)
    
    if isAudio:
        download_file_name = fileName.rsplit(".",1)[0] + ".mp3"
        audio_file_path = os.path.join(YOUTUBE_FILES, download_file_name)
        os.rename(filepath, audio_file_path)
        
    elif stream.is_progressive:
        download_file_name = fileName
    elif not stream.is_progressive:
        download_file_name = fileName.rsplit(".", 1)[0] + "_ytdotin.mp4"
        cmd = f'ffmpeg -i {filepath} -i {audioFilePath} -c:v copy -c:a aac {os.path.join(YOUTUBE_FILES, download_file_name)}'
        subprocess.call(cmd, shell=True)
        removeFile(YOUTUBE_FILES, fileName)
        removeFile(AUDIO_FILES, os.path.basename(audioFilePath))
    
    thread = Timer(delay_in_secs, removeFile, ["False", download_file_name])
    thread.start()
    
    
    
    
def audioDownloadComplete(stream, filepath):
    """ Will convert mp4 to mp3 
    """
    global audioFilePath
    oldAudioFile = filepath
    audioFileName = os.path.basename(filepath)
    audioFileName = secure_filename(audioFileName)
    audioFileName = audioFileName.rsplit(".", 1)[0] + ".mp3"
    audioFilePath = os.path.join(AUDIO_FILES, audioFileName)
    os.rename(filepath, audioFilePath)
    if os.path.exists(oldAudioFile):
        os.remove(oldAudioFile)

    
    
# Get file extension from filename
def get_file_extension(filename):
    if not "." in filename:
        return False
    return filename.rsplit(".",1)[1].upper()


# Check whether the request was for an audio or video
def checkFileRequest(streams, stream_id) -> bool:
    print(streams)
    for i in range(len(streams[0])):
        if str(streams[0][i][0]) == str(stream_id):
            if "audio" in str(streams[0][i][3]):
                return True
            else:
                return False


# Index url for site
@app.route("/", methods=["GET"])
@app.route("/index")
def index():
    return render_template("index.html")

# Details on form POST request and displays streams
@app.route("/details", methods=["POST"])
def details():
    if request.method == "POST":
        try:
            yturl = request.form.get("url")
        except AttributeError as e:
            return redirect("/", 404)

        global yt, streams
        try:
            yt = YoutubeVideo(yturl)
            try:
                streams = yt.get_streams()
                details = yt.get_details()
            except AttributeError as e:
                flash("Enter a valid youtube url!", flush=True)
                return redirect("/")
            return render_template('details.html', streams=streams, details=details)
        except:
            error = sys.exc_info()
            if "get_ytplayer_config" in str(sys.exc_info()[1]):
                flash("Enter valid video url!", "danger" )
            elif "getaddrinfo failed" in str(sys.exc_info()[1]):
                network = False
                flash("Failed to get data. Please check your internet connection", "danger")
            elif "TimeoutError" in str(sys.exc_info()[1]):
                flash("Connection Timeout, took too long to respond! Check your internet connection.", "danger")
            else:
                flash(error, "danger")
            return redirect("/")
    else:
        return redirect("/")

#On visiting this with stream id it will redirect to send it from dir
@app.route("/download/<string:stream_id>", methods=["GET"])
def download(stream_id):
    global yt, downloadStatus, download_file_name, streams, isAudio, is_notProgressive, audioDownloadStart
    isAudio = checkFileRequest(streams, stream_id)
    for i in range(len(streams[0])):
        if str(streams[0][i][0]) == str(stream_id):
            if not yt.is_progressive(stream_id):
                is_notProgressive = True
    try:
        if is_notProgressive:
            yt.download_complete(audioDownloadComplete)
            yt.downloadAudio(AUDIO_FILES)
        yt.download_complete(redirectUser)
        yt.download(int(stream_id), YOUTUBE_FILES)
    except AttributeError as e:
        flash("Something went wrong, please try again!")
        return redirect("/")
    return render_template("download.html", downloadStatus=downloadStatus, fileName=download_file_name)


#Send the file from dir
@app.route("/download/f/<string:file_name>", methods=["GET"])
def returnFile(file_name):
    return send_from_directory(YOUTUBE_FILES, file_name, as_attachment=True)


@app.errorhandler(404)
def pagenotFound(error):
    return render_template("404.html")

@app.errorhandler(405)
def methodNotAllowed(error):
    return render_template("405.html")

if __name__ == "__main__":
    app.run(debug=True, port=5001)
