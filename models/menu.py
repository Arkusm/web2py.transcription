# -*- coding: utf-8 -*-

global response, T, URL

response.title = 'Transcribe'
response.subtitle = 'Transcribe audio and video'
response.meta.author = 'Markus Schmidt'
response.meta.description = 'describe your app'
response.meta.keywords = 'Application for transcribing media data'
response.logourl = URL('default', 'index')

response.menu = [
    (T('Home'), False, URL('default', 'index'), []),
    (T('Manage media'), False, URL('default', 'manage'), [])
]

