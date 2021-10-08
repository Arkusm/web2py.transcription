# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------
# This is a sample controller
# this file is released under public domain and you can use without limitations
# -------------------------------------------------------------------------

#from transcription_tools import create_vtt
transcription_tools = local_import('transcription_tools', reload=True)

# ---- example index page ----
def index():
    media_files = db().select(db.media_file.ALL, orderby=db.media_file.title)
    return dict(media_files=media_files)

@auth.requires_membership('manager')
def manage():   
    grid = SQLFORM.smartgrid(db.media_file, linked_tables=['post'])
    return dict(grid=grid)

def vtt():
    return dict(message=transcription_tools.create_vtt(
        '/home/mschmidt/Videos/100-Meinungen-Video-erstellen.mp4'))

def user():
    return dict(form=auth())