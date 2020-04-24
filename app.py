from flask import Flask, request, Response, jsonify
from generator import fetch_config, fetch_font_map, form_font_face

app = Flask(__name__)

"""
ABOUT ROUTING

In Fontiles' current revision, all fonts have determined
paths for all resources.

Full Font family (all members):
$HOST/fonts/$FONT_SLUG/full.css

TTF static source:
$HOST/fonts/$FONT_SLUG/static/$MEMBER_SLUG.ttf

Font Family Config:
$HOST/fonts/$FONT_SLUG/font.json

In addition, all Fontiles instances have a /ping
route that returns a text response 'pong' and others:

App Config:
$HOST/config.json
"""

@app.route('/')
def hello():
    return 'test world'

@app.route('/ping')
def ping():
    return 'pong'

@app.route('/config.json')
def config():
    return jsonify(fetch_config())

@app.route('/fonts/<font_slug>/font.json')
def font_config(font_slug):
    return jsonify(fetch_font_map(font_slug))

@app.route('/fonts/<font_slug>/LICENSE')
def font_license(font_slug):
    return jsonify("not implemented.")

@app.route('/fonts/<font_slug>/full.css')
def font_full_css(font_slug):
    cfg = fetch_config()
    fcfg = fetch_font_map(font_slug)
    member_css = []

    if not fcfg:
        return Response("""/**
 * generated by Fontiles, served from {}
 * font {} does not exist
**/
""".format(cfg["name"], font_slug), mimetype='text/css')

    for member in fcfg["members"]:
        member_css += [form_font_face(cfg["host"], fcfg, member)]

    return Response("""/**
 * generated by Fontiles, served from {}
 * font: {}
 * author: {}
**/

{}
""".format(cfg["name"], fcfg["name"], fcfg["author"],
"\n\n".join(member_css)), mimetype='text/css')