# REQUIREMENTS

* ffmpeg
* git
* python3
* pip3
* python module srt
* python module vosk
* language model

# INSTALL UBUNTU

```
apt install ffmpeg
apt install python3-pip
pip3 install --upgrade pip
cd /usr/lib/
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