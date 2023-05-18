from flask import Blueprint, render_template, request, flash, url_for, jsonify,redirect, current_app
from .models import ytVideos
from .models import tfVersions
from .models import ytClips
from . import db
from json import dumps
from urllib.parse import urlencode
import requests
import git

from datetime import datetime,timezone
from dateutil.relativedelta import relativedelta
from dateutil import parser as dtparser
import pytz
import urllib.parse

from webargs import  validate
from webargs.flaskparser import parser, abort, use_args
from marshmallow import Schema, fields, EXCLUDE, missing


forms = Blueprint("forms", __name__)


# Return validation errors as JSON
@forms.errorhandler(422)
@forms.errorhandler(400)
def handle_error(err):
    
    headers = err.data.get("headers", None)
    messages = err.data.get("messages", ["Invalid request."])
    if headers:
        
        return jsonify({"errors": messages}), err.code, headers
    else:
        return jsonify({"errors": messages}), err.code

mrtf_languages = (1)

class ytFormSchema(Schema):
    yt_video_id= fields.Str(required=True)
    yt_account= fields.Str()
    yt_channel_id= fields.Str()
    yt_published_date= fields.Str()
    yt_video_title= fields.Str()
    yt_stats_comments= fields.Int()
    yt_stats_favorites= fields.Int()
    yt_stats_likes= fields.Int()
    yt_stats_views= fields.Int()
    yt_channel_image= fields.URL()
    yt_channel_title= fields.Str()
    yt_stats_lastupdated= fields.Str()
    st_creator_name= fields.Str()
    st_creator_id= fields.Str()
    st_presenter_id= fields.Str()
    st_presenter_name= fields.Str()
    st_haspresenter= fields.Int()
    tf_match_format = fields.Str(validate=[validate.OneOf(['sixes','highlander','prolander','bball','ultiduo','other'])])
    tf_map_full= fields.Str()
    tf_version_full= fields.Str()
    tf_resource_type = fields.Str(validate=[validate.OneOf(['Map Review','Demo Review','Live POV','Guide','Callout Guide','Rollout Guide','Jump Guide','Frag Video','Other'])])
    tf_class_all= fields.Int()
    tf_class_none= fields.Int()
    tf_class_scout= fields.Int()
    tf_class_soldier= fields.Int()
    tf_class_pyro= fields.Int()
    tf_class_demo= fields.Int()
    tf_class_heavy= fields.Int()
    tf_class_engineer= fields.Int()
    tf_class_medic= fields.Int()
    tf_class_spy= fields.Int()
    tf_class_sniper= fields.Int()
    tf_role_combo= fields.Int()
    tf_role_flank= fields.Int()
    tf_role_offclass= fields.Int()
    tf_skill_level = fields.Str(validate=[validate.OneOf(['NC/AM','IM/MAIN','AD/INV'])])
    tf_league = fields.Str(validate=[validate.OneOf(['RGL','ETF2L','AsiaFortress','ozfortress','UGC','ESEA','other'])])
    tf_has_teamcoms= fields.Int()
    mrtf_language= fields.Str(validate=[validate.OneOf(['Arabic', 'Bulgarian', 'Chinese (Mandarin)', 'Croatian', 'Czech', 'Danish', 'Dutch', 'English', 'Finnish', 'French', 'German', 'Greek', 'Hindi', 'Hungarian', 'Icelandic', 'Indonesian', 'Irish', 'Italian', 'Japanese', 'Korean', 'Norwegian', 'Polish', 'Portuguese', 'Romanian', 'Russian', 'Serbian', 'Slovak', 'Slovenian', 'Spanish', 'Swedish ', 'Turkish', 'Ukrainian', 'Vietnamese'])])
    tf_map_full_provisional = fields.Str()
    tf_version_full_provisional =fields.Str()

    class Meta:
        unknown = EXCLUDE


tf_version_args = {
    "tf_match_format" : fields.Str(validate=[validate.OneOf(['sixes','highlander','prolander','bball','ultiduo','other'])]),
    "tf_map_name": fields.Str(),
    "tf_map_full": fields.Str(),
    "tf_version_full": fields.Str(),
    "tf_map_full_provisional": fields.Str(),
    "tf_version_full_provisional": fields.Str()
}



@forms.route('/video', methods=['POST','GET'])
def submit_video():
    #tf_version_full	version_order	version_iscurrent	tf_map_full	map_name
    #tf_versions
    tf_version_full_list = db.session.query(tfVersions).order_by(tfVersions.tf_version_release_date.desc())
    tf_versions = db.session.execute(db.select(tfVersions.tf_map_full,tfVersions.tf_map_name).distinct().order_by(tfVersions.tf_map_name))
    #tf_version_full_list = list(Versions.query.all().order_by(Versions.version_order.desc()))
    #tf_version_full_list = sorted([("cp_sunshine","cp_sunshine_rc9",1,False),("cp_sunshine","cp_sunshine",3,True),("cp_sunshine","cp_sunshine_rc10",2,False)],key=lambda x: x[2],reverse = True)
    title_text = "TF2 Map Review - Submit Video"
    return render_template("./submit_video.html",tf_versions=tf_versions,tf_version_full_list=tf_version_full_list,title_text=title_text)

@forms.route('/clip', methods=['POST','GET'])
def submit_clip():
    tf_version_full_list = db.session.query(tfVersions).order_by(tfVersions.tf_version_release_date.desc())
    tf_versions = set(db.session.execute(db.select(tfVersions.tf_map_full,tfVersions.tf_map_name)))
    return render_template("./submit_clip.html",tf_versions=tf_versions,tf_version_full_list=tf_version_full_list)


def add_tf_map_version(tf_map_name, tf_map_full):
    _version = tfVersions()
    try:
        if tf_map_full.split("_")[0] in ['koth','cp']:
            setattr(_version,"tf_map_format",tf_map_full.split("_")[0])
    except:
        pass

    setattr(_version,"tf_map_name",tf_map_name)
    setattr(_version,"tf_map_full",tf_map_full)
    #setattr(_version,"tf_version_full",tf_map_full)
    setattr(_version,"tf_version_provisional",True)


    db.session.add(_version)
    db.session.commit()
    print(f"Submitted {tf_map_full} to database")
    return


def is_yt_video_id_valid(yt_video_id):
    print(yt_video_id)
    '''Check with YouTube v3 API if yt_video_id is valid. Return {'count':1} if it is else {'count':0} if it isnt'''
    print(f"yt_video_id: {yt_video_id}")
    search_url = "https://www.googleapis.com/youtube/v3/videos"
    search_params = {'key': current_app.config["YOUTUBE_API_KEY"],'part':"snippet","id":yt_video_id}
    r = requests.get(search_url,search_params)
    print(r.json())
    return True if r.json()['pageInfo']['totalResults'] == 1 else False
    

def is_yt_video_id_in_database(yt_video_id):
    _videos = db.session.query(ytVideos).filter(ytVideos.yt_video_id.in_([yt_video_id]))
    return True if len(list(_videos)) > 0 else False
    
    
@forms.route('/submit_yt_video', methods=['POST'])
@use_args(ytFormSchema(), location='form', unknown=None)
def submit_yt_form(args):
    '''Accept POST request for YouTube Video forms'''
    print(f"args: {args}")
    _vid = ytVideos()
    setattr(_vid,'mrtf_upload_datetime',datetime.now())
    tf_map_full_provisional, tf_version_provisional = None, None
    for k,v in args.items():
        #use dateutil.parse to parse dates - more robust than webargs/marshmallow
        if 'date' in k:
            v = dtparser.parse(v)
        if 'tf_map_full_provisional' in k:
            tf_map_full_provisional = v
            continue
        if 'tf_version_provisional' in k:
            tf_version_provisional = v
            continue
        setattr(_vid,k,v)

    if tf_map_full_provisional:
        add_tf_map_version(tf_map_full_provisional,tf_version_provisional)
    try:
        print(str(request.headers.get('X-Forwarded-For'))) #PythonAnywhere forwards ip requests in headder from local IP
        setattr(_vid,"mrtf_upload_ip",str(request.headers.get('X-Forwarded-For')))
    except:
        print('ipgetttingfailed')

    #validate objects
    if is_yt_video_id_in_database(_vid.yt_video_id):
        return 'YouTube Video already in Database', 400
    
    if not is_yt_video_id_valid(_vid.yt_video_id):
        return 'Invalid YouTube Video ID',400
    #setattr(_clip,"mrtf_upload_steam_id",<steamidvar>)
    field_class_dic = {"tf_class_scout":"Scout","tf_class_soldier":"Soldier","tf_class_pyro":"Pyro","tf_class_demo":"Demoman","tf_class_heavy":"Heavy","tf_class_engineer":"Engineer","tf_class_medic":"Medic","tf_class_sniper":"Sniper","tf_class_spy":"Spy"}

    _relevant_class_list = []
    for _f,_c in field_class_dic.items():
        if getattr(_vid,_f):
            _relevant_class_list.append(_c)


    #update algorithm
    days_old = (datetime.now(timezone.utc) - _vid.yt_published_date).days
    age_score = (1-min(1.0,days_old/2191))**4
    likes_score = min(1,(float(_vid.yt_stats_likes)/100)**0.5)
    views_score = min(1,(float(_vid.yt_stats_views)/2000))
    ratio_score = max(1.0,10*float(_vid.yt_stats_likes)/float(_vid.yt_stats_views))

    mrtf_rating_score_a1 = int(100*(age_score*2 + likes_score + views_score + ratio_score)/5)
    setattr(_vid,"mrtf_rating_score_a1",mrtf_rating_score_a1)
    #yt_stats_comments

    if len(_relevant_class_list) == 1:
        setattr(_vid,"relevant_classes",_relevant_class_list[0])

    db.session.add(_vid)
    db.session.commit()
    return '',200



@forms.route('/submit_yt_clip', methods=['POST'])
def submit_yt_clip_form():
    #TODO add validation from submit_yt_videos
    _clip = ytClips()
    for k,v in request.form.items():
        k = k.replace("[]","")
        if isinstance(v, list):
             v = v[0]
        if 'date' in k:
            v = dtparser.parse(v)
        print(k,v)
        setattr(_clip,k,v)
    print("mrtf_upload_ip: ",str(request.remote_addr))
    setattr(_clip,'mrtf_upload_datetime',datetime.now())
    setattr(_clip,"mrtf_upload_ip",str(request.remote_addr))
    #setattr(_clip,"mrtf_upload_steam_id",<steamidvar>)
    print(_clip)
    db.session.add(_clip)
    db.session.commit()
    return '',200

@forms.errorhandler(422)
@forms.errorhandler(400)
def handle_error(err):
    headers = err.data.get("headers", None)
    messages = err.data.get("messages", ["Invalid request."])
    if headers:
        print(jsonify({"errors": messages}), err.code, headers)
        return jsonify({"errors": messages}), err.code, headers
    else:
        print(err.data)
        print(jsonify({"errors": messages}), err.code)
        return jsonify({"errors": messages}), err.code

