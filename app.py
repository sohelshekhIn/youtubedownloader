from flask import Flask, request, render_template, send_from_directory, Response, redirect, flash
from YoutubeDownload import YoutubeVideo
from threading import Timer
from datetime import datetime
import os
import sys

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
YOUTUBE_FILES = "YouTube_Files"



# Remove the downloaded file from the directory
def removeFile(fileName):
    os.remove(os.path.join(YOUTUBE_FILES, fileName))

# Download Status to True for redirection and run remove file function
def redirectUser(stream, filepath):
    global downloadStatus, download_file_name, isAudio
    downloadStatus = True
    download_file_name = os.path.basename(filepath)
    if isAudio:
        download_file_name = os.path.splitext(download_file_name)[0] + ".mp3"
        audio_file_path = os.path.join(YOUTUBE_FILES, download_file_name)
        os.rename(filepath, audio_file_path)
    
    thread = Timer(delay_in_secs, removeFile, [download_file_name])
    thread.start()
    

# Get file extension from filename
def get_file_extension(filename):
    if not "." in filename:
        return False

    return filename.rsplit(".",1)[1].upper()


# Check whether the request was for an audio or video
def checkFileRequest(streams, stream_id):
    for i in range(len(streams)):
        if str(streams[i][0]) == str(stream_id):
            if "audio" in str(streams[i][3]):
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
        except AttributeError as a:
            return redirect("/", 404)

        global yt, streams
        try:
            yt = YoutubeVideo(yturl)
        except:
            error = sys.exc_info()
            if "get_ytplayer_config" in str(sys.exc_info()[1]):
                flash("Enter valid video url!")
                return redirect("/")
            elif "getaddrinfo failed" in str(sys.exc_info()[1]):
                network = False
                flash("Failed to get data. Please check your internet connection", "danger")
                return redirect("/")
            else:
                flash(error, "danger")
                redirect("/")
        try:
            streams = yt.get_streams()
            details = yt.get_details()
        except AttributeError as e:
            flash("Enter a valid youtube url!")
            return redirect("/")
        return render_template('details.html', streams=streams, details=details)
    else:
        return redirect("/")

#On visiting this with stream id it will redirect to send it from dir
@app.route("/download/<string:stream_id>", methods=["GET"])
def download(stream_id):
    global yt, downloadStatus, download_file_name, streams, isAudio
    isAudio = checkFileRequest(streams, stream_id)
    try:
        yt.download_complete(redirectUser)
        yt.download(stream_id, YOUTUBE_FILES)
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
    app.run(debug=True)
