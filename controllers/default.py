# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------
# This is a sample controller
# this file is released under public domain and you can use without limitations
# -------------------------------------------------------------------------

import io
#from transcription_tools import create_vtt
transcription_tools = local_import('transcription_tools', reload=True)

model = 'private/model'


# ---- example index page ----
def index():
    media_files = db().select(db.media_file.ALL, orderby=db.media_file.title)
    return dict(media_files=media_files)


@auth.requires_membership('manager')
def manage():
    grid = SQLFORM.smartgrid(db.media_file, linked_tables=['post'])
    return dict(grid=grid)


def webvtt_single_line():
    media_file = db.media_file(request.args(0, cast=int)) or redirect(URL('index'))
    media_path = '{}/{}/{}'.format(request.folder, 'uploads', media_file.file)
    model_path = '{}/{}'.format(request.folder, model)
    transkription = transcription_tools.vtt_single_line(model_path, media_path)
    db(db.media_file.id == media_file.id).update(vtt_single_line=transkription)
    redirect(request.env.http_referer)

def webvtt():
    media_file = db.media_file(request.args(0, cast=int)) or redirect(URL('index'))
    media_path = '{}/{}/{}'.format(request.folder, 'uploads', media_file.file)
    model_path = '{}/{}'.format(request.folder, model)
    transkription = transcription_tools.vtt(model_path, media_path)
    db(db.media_file.id == media_file.id).update(vtt=transkription)
    redirect(request.env.http_referer)


def download_webvtt_single_line():
    media_file = db.media_file(request.args(0, cast=int)) or redirect(URL('index'))
    webvtt = media_file.vtt_single_line
    response.headers['Content-Type']='text/vtt'
    response.headers['Content-Disposition']='attachment; filename=transcript.vtt'
    f = io.StringIO(webvtt)
    return(f)

def download_webvtt():
    media_file = db.media_file(request.args(0, cast=int)) or redirect(URL('index'))
    webvtt = media_file.vtt
    response.headers['Content-Type']='text/vtt'
    response.headers['Content-Disposition']='attachment; filename=transcript.vtt'
    f = io.StringIO(webvtt)
    return(f)


def user():
    return dict(form=auth())
