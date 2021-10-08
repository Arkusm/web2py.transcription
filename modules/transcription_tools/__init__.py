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
import sys
import os
import wave
import subprocess
import srt
import json
import datetime


def create_vtt():
    sample_rate = 16000
    model = Model("applications/transcription/private/model")
    rec = KaldiRecognizer(model, sample_rate)
    rec.SetWords(True)

    process = subprocess.Popen(['ffmpeg', '-loglevel', 'quiet', '-i',
                                '/home/mschmidt/Videos/100-Meinungen-Video-erstellen.mp4',
                                '-ar', str(sample_rate) , '-ac', '1', '-f', 's16le', '-'],
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
                line = words[j : j + WORDS_PER_LINE] 
                s = srt.Subtitle(index=len(subs), 
                    content=" ".join([l['word'] for l in line]),
                    start=datetime.timedelta(seconds=line[0]['start']), 
                    end=datetime.timedelta(seconds=line[-1]['end']))
                subs.append(s)
        return subs

    return (srt.compose(transcribe()))

