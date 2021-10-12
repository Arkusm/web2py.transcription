# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------
# REQUIREMENTS
#
# module srt
# module vosk
# language model
#
# INSTALL
#
# apt install ffmpeg
# apt install python3-pip
# pip3 install --upgrade pip
# cd /usr/lib/
# git clone --recursive https://github.com/web2py/web2py.git
# cd web2py/applications
# mkdir transcription
# cd transcription
# git clone https://gitea.iwm-tuebingen.de/mschmidt/web2py.transcription.git .
# pip3 install -t modules srt
# pip3 install -t modules vosk
# pip3 install -t modules webvtt-py
# cd private
# wget https://alphacephei.com/vosk/models/vosk-model-de-0.21.zip
# unzip vosk-model-de-0.21.zip
# -------------------------------------------------------------------------

import io
from vosk import KaldiRecognizer
from webvtt import WebVTT, Caption
import subprocess
import srt
import json
import datetime
import textwrap
import transcription_tools
# transcription_tools = local_import('transcription_tools', reload=True)

# To let Eclipse know about predefined objects
global db
global request
global session
global reqponse
global SQLFORM
global redirect
global auth
global URL
global response


model_mod_path = 'private/model'


def index():
    media_files = db().select(db.media_file.ALL, orderby=db.media_file.title)
    return dict(media_files=media_files)


@auth.requires_membership('manager')
def manage():
    grid = SQLFORM.smartgrid(db.media_file, linked_tables=['post'])
    return dict(grid=grid)


def webvtt_single_line():
    # Get mediafile from request
    media_file = (db.media_file(request.args(0, cast=int)) or
                  redirect(URL('index')))
    # Set vars
    media_path = '{}/{}/{}'.format(request.folder, 'uploads', media_file.file)
    model_path = '{}/{}'.format(request.folder, model_mod_path)

    # Trascribe to SubRip Subtitle file SRT
    sample_rate = 16000
    model = transcription_tools.get_model(model_path)
    rec = KaldiRecognizer(model, sample_rate)
    rec.SetWords(True)

    # 16bit mono with ffmpeg
    process = subprocess.Popen(
        ['ffmpeg', '-loglevel', 'quiet', '-i', media_path, '-ar',
         str(sample_rate), '-ac', '1', '-f', 's16le', '-'],
        stdout=subprocess.PIPE
    )

    WORDS_PER_LINE = 7

    def transcribe():
        results = []
        subs = []
        while True:
            data = process.stdout.read(4000)
            if len(data) == 0:
                break
            if rec.AcceptWaveform(data):
                results.append(rec.Result())
        results.append(rec.FinalResult())

        for i, res in enumerate(results):
            jres = json.loads(res)
            if not 'result' in jres:
                continue
            words = jres['result']
            for j in range(0, len(words), WORDS_PER_LINE):
                line = words[j: j + WORDS_PER_LINE]
                s = srt.Subtitle(
                    index=len(subs),
                    content=" ".join([l['word'] for l in line]),
                    start=datetime.timedelta(seconds=line[0]['start']),
                    end=datetime.timedelta(seconds=line[-1]['end'])
                )
                subs.append(s)
        return subs

    srt_str = srt.compose(transcribe())  # create srt string

    # Create single line webvtt from srt with ffmepg
    process1 = subprocess.Popen(
        ['ffmpeg', '-loglevel', 'quiet', '-i', '-', '-f', 'webvtt', '-'],
        stdin=subprocess.PIPE, stdout=subprocess.PIPE
    )
    # Send srt_str as input file to ffmpeg process
    webvtt = process1.communicate(input=bytes(srt_str, 'utf-8'))[0]

    # Add result to database
    db(db.media_file.id == media_file.id).update(vtt_single_line=webvtt)
    redirect(request.env.http_referer)


def webvtt():
    # Get mediafile from request
    media_file = (db.media_file(request.args(0, cast=int)) or
                  redirect(URL('index')))
    # Set vars
    media_path = '{}/{}/{}'.format(request.folder, 'uploads', media_file.file)
    model_path = '{}/{}'.format(request.folder, model_mod_path)

    # Transcribe
    sample_rate = 16000
    model = transcription_tools.get_model(model_path)  # cached model
    rec = KaldiRecognizer(model, sample_rate)
    rec.SetWords(True)

    def timeString(seconds):
        minutes = seconds / 60
        seconds = seconds % 60
        hours = int(minutes / 60)
        minutes = int(minutes % 60)
        return '%i:%02i:%06.3f' % (hours, minutes, seconds)

    def transcribe():
        command = ['ffmpeg', '-nostdin', '-loglevel', 'quiet', '-i',
                   media_path, '-ar', str(sample_rate), '-ac', '1', '-f',
                   's16le', '-']
        process = subprocess.Popen(command, stdout=subprocess.PIPE)

        results = []
        while True:
            data = process.stdout.read(4000)
            if len(data) == 0:
                break
            if rec.AcceptWaveform(data):
                results.append(rec.Result())
        results.append(rec.FinalResult())

        vtt = WebVTT()
        for i, res in enumerate(results):
            words = json.loads(res).get('result')
            if not words:
                continue

            start = timeString(words[0]['start'])
            end = timeString(words[-1]['end'])
            content = ' '.join([w['word'] for w in words])

            caption = Caption(start, end, textwrap.fill(content))
            vtt.captions.append(caption)

        return(vtt.content)

    # Write result to database
    db(db.media_file.id == media_file.id).update(vtt=transcribe())
    redirect(request.env.http_referer)


def download_webvtt_single_line():

    media_file = (db.media_file(request.args(0, cast=int)) or
                  redirect(URL('index')))

    webvtt = media_file.vtt_single_line

    response.headers['Content-Type'] = 'text/vtt'
    response.headers['Content-Disposition'] = ('attachment; '
                                               'filename=transcript.vtt')

    f = io.StringIO(webvtt)

    return(f)


def download_webvtt():

    media_file = (db.media_file(request.args(0, cast=int)) or
                  redirect(URL('index')))

    webvtt = media_file.vtt

    response.headers['Content-Type'] = 'text/vtt'
    response.headers['Content-Disposition'] = ('attachment; '
                                               'filename=transcript.vtt')

    f = io.StringIO(webvtt)

    return(f)


def user():
    return dict(form=auth())
