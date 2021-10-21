web2py.transcription is a web application based on web2py for transcribing audio and video files. The core of the application is the speech recognition toolkit vosk.

# Requirements

* ffmpeg
* git
* python3
* pip3
* python module srt
* python module vosk
* python module webvtt-py
* vosk language model

# Install on Ubuntu

The following steps install the application to ~/web2py

```
apt install ffmpeg
apt install python3-pip
pip3 install --upgrade pip
cd ~
git clone --recursive https://github.com/web2py/web2py.git
cd web2py/applications
mkdir transcription
cd transcription
git clone https://gitea.iwm-tuebingen.de/mschmidt/web2py.transcription.git .
pip3 install -t modules srt
pip3 install -t modules vosk
pip3 install -t modules webvtt-py
cd private
wget https://alphacephei.com/vosk/models/vosk-model-de-0.21.zip
unzip vosk-model-de-0.21.zip
mv vosk-model-de-0.21 model
```

# Start

```
cd ~/web2py
python3 web2py
```
Assign administrator password.

# Usage

The application works only for logged-in users with the role 'manager' !

* Point your webbrowser to http://localhost:8000/transcription
* Register a user by clicking login->register on the top right side.
* Point your webbrowser to http://localhost:8000/transcription/appadmin
* Log in with the administrator password you assigned at startup.
* Click on db.auth_group -> New entry
* Create the new Entry 'manager'
* Go back to http://localhost:8000/transcription/appadmin
* Click on db.auth_membership -> New entry
* Click and select your user id in the first field and the new group 'manager' in the scond field