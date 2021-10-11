# REQUIREMENTS
#
# module srt
# module vosk
# language model
#
# INSTALL
#
# cd web2py/applications/transcription
# pip3 install -t modules srt
# pip3 install -t modules vosk
# cd private
# wget https://alphacephei.com/vosk/models/vosk-model-de-0.21.zip
# unzip vosk-model-de-0.21.zip


from vosk import Model, KaldiRecognizer, SetLogLevel
from webvtt import WebVTT, Caption
import sys
import os
import wave
import subprocess
import srt
import json
import datetime
import textwrap


def vtt_single_line(model_path, media_path):
    sample_rate = 16000
    model = Model(model_path)
    rec = KaldiRecognizer(model, sample_rate)
    rec.SetWords(True)

    # 16bit mono with ffmpeg
    process = subprocess.Popen(['ffmpeg', '-loglevel', 'quiet', '-i',
                                media_path,
                                '-ar', str(sample_rate),
                                '-ac', '1', '-f', 's16le', '-'],
                                stdout=subprocess.PIPE)

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

    # webvtt from srt with ffmepg
    process1 = subprocess.Popen(
        ['ffmpeg', '-loglevel', 'quiet', '-i', '-', '-f', 'webvtt', '-'],
        stdin=subprocess.PIPE, stdout=subprocess.PIPE
        )

    webvtt = process1.communicate(input=bytes(srt_str, 'utf-8'))[0]

    return (webvtt)


def vtt(model_path, media_path):
    sample_rate = 16000
    model = Model(model_path)
    rec = KaldiRecognizer(model, sample_rate)
    rec.SetWords(True)

    WORDS_PER_LINE = 7

    def timeString(seconds):
        minutes = seconds / 60
        seconds = seconds % 60
        hours = int(minutes / 60)
        minutes = int(minutes % 60)
        return '%i:%02i:%06.3f' % (hours, minutes, seconds)

    def transcribe():
        command = ['ffmpeg', '-nostdin', '-loglevel', 'quiet', '-i', media_path,
                   '-ar', str(sample_rate), '-ac', '1', '-f', 's16le', '-']
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

    return(transcribe())
