from flask import Blueprint, render_template, request, flash, url_for, jsonify,redirect, current_app, send_from_directory
from .models import ytVideos, tfVersions, ytClips, ytChapters, mrtfVotes, mrtfHackerTracker
from . import db
import json
from urllib.parse import urlencode, urlparse, parse_qsl
import requests
import git
from datetime import datetime, timezone
from dateutil import parser as dtparser
import pytz
import urllib.parse
import operator

from sqlalchemy import or_, and_
from sqlalchemy import func, distinct
from sqlalchemy.orm import lazyload

from sqlalchemy.sql import label

from flask_session import Session
from flask import session

from webargs import fields, validate
from webargs.flaskparser import parser
from webargs.flaskparser import abort

views = Blueprint("views", __name__)


@views.route('/robots.txt')
def static_from_root():
    '''Return static text documents'''
    return send_from_directory('static/txt/', request.path[1:])

@views.route('/webhook', methods=['POST'])
def webhook():
    '''Github Webhook for autoupdating server repo'''
    if request.method == 'POST':
        print(request) 
        repo = git.Repo('./mapreview.tf')
        repo.git.reset('--hard')
        origin = repo.remotes.origin
        #repo.create_head('master', origin.refs.main).set_tracking_branch(origin.refs.main).checkout()
        origin.pull()
        return '', 200
    else:
        return ''
    
@views.route('/', methods=['GET'])
def browse_home():
    arg_dic = request.args.to_dict(flat=False)
    #populate list of existing maps in Videos
    tf_maps = list(set(db.session.execute(db.select(ytVideos.tf_map_full).order_by(ytVideos.tf_map_full)).scalars()))
    tf_versions = list(set(db.session.execute(db.select(tfVersions.tf_map_full, tfVersions.tf_map_name))))
    yt_creators = list(set(db.session.execute(db.select(ytVideos.mrtf_display_name,ytVideos.mrtf_display_id))))
    relevant_roles = (("Roamer&Flank","Roamer/Flank"),("Combo&Pocket","Combo/Pocket"),("Offclass","Offclass"))
    relevant_classes =("Scout","Soldier","Demo","Medic")
    #relevant_classes = zip(*list(set(db.session.execute(db.select(ytVideos.tf_role,ytVideos.relevant_classes)))))
    resource_types = [rt[0] for rt in list(set(db.session.execute(db.select(ytVideos.tf_resource_type))))]
    mrtf_languages = [l[0] for l in list(set(db.session.execute(db.select(ytVideos.mrtf_language))))]
    
    meta_dic = {"description":"TF2 Competitive Sixes and Highlander Map Reviews showcasing community-created resources for all RGL/ETF2L/ozfortress/AsiaFortress rotation maps including Process, Sunshine, Gullywash, Metalworks, Sultry, ClearCut, Reckoner, Snakewater, Villa, Bagel, Badlands, Granary and more map reviews, class guides, and community made resources for Soldier, Demo, Scout, and Medic"}
    title_text = "TF2 Map Review - Home"

    return render_template("./browse.html", format_sixes = True, tf_maps=tf_maps,tf_versions=tf_versions,yt_creators = yt_creators,relevant_roles=relevant_roles,relevant_classes=relevant_classes,resource_types=resource_types,mrtf_languages=mrtf_languages,meta_dic=meta_dic,title_text=title_text)


@views.route('/sixes', methods=['GET'])
def browse_sixes():
    arg_dic = request.args.to_dict(flat=False)
    #populate list of existing maps in Videos
    tf_maps = list(set(db.session.execute(db.select(ytVideos.tf_map_full).order_by(ytVideos.tf_map_full)).scalars()))
    tf_versions = list(set(db.session.execute(db.select(tfVersions.tf_map_full, tfVersions.tf_map_name))))
    yt_creators = list(set(db.session.execute(db.select(ytVideos.mrtf_display_name,ytVideos.mrtf_display_id))))
    relevant_roles = (("Roamer&Flank","Roamer/Flank"),("Combo&Pocket","Combo/Pocket"),("Offclass","Offclass"))
    relevant_classes =("Scout","Soldier","Demo","Medic")
    #relevant_classes = zip(*list(set(db.session.execute(db.select(ytVideos.tf_role,ytVideos.relevant_classes)))))
    resource_types = [rt[0] for rt in list(set(db.session.execute(db.select(ytVideos.tf_resource_type))))]
    mrtf_languages = [l[0] for l in list(set(db.session.execute(db.select(ytVideos.mrtf_language))))]
    
    meta_dic = {"description":"TF2 Competitive Sixes Map Reviews showcasing community-created resources for all RGL/ETF2L/ozfortress/AsiaFortress rotation maps including Process, Sunshine, Gullywash, Metalworks, Sultry, ClearCut, Reckoner, Snakewater, Villa, Bagel, Badlands, Granary and more map reviews, class guides, and community made resources for Soldier, Demo, Scout, and Medic"}
    title_text = "TF2 Map Review - Sixes"

    return render_template("./browse.html", format_sixes = True, tf_maps=tf_maps,tf_versions=tf_versions,yt_creators = yt_creators,relevant_roles=relevant_roles,relevant_classes=relevant_classes,resource_types=resource_types,mrtf_languages=mrtf_languages,meta_dic=meta_dic,title_text=title_text)


@views.route('/highlander', methods=['GET'])
def browse_highlander():
    arg_dic = request.args.to_dict(flat=False)
    #populate list of existing maps in Videos
    tf_maps = list(set(db.session.execute(db.select(ytVideos.tf_map_full).order_by(ytVideos.tf_map_full)).scalars()))
    tf_versions = list(set(db.session.execute(db.select(tfVersions.tf_map_full, tfVersions.tf_map_name))))
    yt_creators = list(set(db.session.execute(db.select(ytVideos.mrtf_display_name,ytVideos.mrtf_display_id))))
    relevant_roles = (("Roamer/Flank","Flank"),("Combo&Pocket","Combo/Pocket"),("Offclass","Offclass"))
    relevant_classes = ("Scout","Soldier","Pyro","Demoman","Heavy","Engineer","Medic","Sniper","Spy")
    #relevant_classes = zip(*list(set(db.session.execute(db.select(ytVideos.tf_role,ytVideos.relevant_classes)))))

    resource_types = [rt[0] for rt in list(set(db.session.execute(db.select(ytVideos.tf_resource_type))))]
    mrtf_languages = [l[0] for l in list(set(db.session.execute(db.select(ytVideos.mrtf_language))))]
    meta_dic = {"description":"TF2 Competitive Highlander Map Reviews showcasing community-created resources for all RGL/ETF2L/ozfortress/AsiaFortress rotation maps including KOTH Ashville, Cascade, Lakeside, Product, Proot, Warmtic, Payload PL Badwater, Borneo, Eruption, Swiftwater, Upward, Vigil  and more map reviews, class guides, and community made resources for Scout, Solider, Pyro, Demo, Engineer, Heavy, Medic, Sniper, Spy and more."}
    title_text = "TF2 Map Review - Highlander"
    alert_text = "Help grow the content here by submitting a video!"
    return render_template("./browse.html", format_sixes = False,tf_maps=tf_maps,tf_versions=tf_versions,yt_creators = yt_creators,relevant_roles=relevant_roles,relevant_classes=relevant_classes,resource_types=resource_types,mrtf_languages=mrtf_languages,alert_text=alert_text,meta_dic=meta_dic,title_text=title_text)

    
    meta_dic = {"description":"TF2 Competitive Sixes Map Reviews showcasing community-created resources for all RGL/ETF2L/ozfortress/AsiaFortress rotation maps including Process, Sunshine, Gullywash, Metalworks, Sultry, ClearCut, Reckoner, Snakewater, Villa, Bagel, Badlands, Granary and more map reviews, class guides, and community made resources for Soldier, Demo, Scout, and Medic"}
    title_text = "TF2 Map Review - Sixes"




def get_yt_video_counts(q):    
    #map
    tf_map_full_count_query = q.statement.with_only_columns([(ytVideos.tf_map_full),func.count(ytVideos.tf_map_full).label('count')]).group_by(ytVideos.tf_map_full).order_by(None)
    print(tf_map_full_count_query)
    #match format
    tf_match_format_count_query = q.statement.with_only_columns([(ytVideos.tf_match_format),func.count(ytVideos.tf_match_format).label('count')]).group_by(ytVideos.tf_match_format).order_by(None)
    
    #type
    tf_resource_type_count_query = q.statement.with_only_columns([(ytVideos.tf_resource_type),func.count(ytVideos.tf_resource_type).label('count')]).group_by(ytVideos.tf_resource_type).order_by(None)
    
    #role
    #tf_role_count_query = q.statement.with_only_columns([(ytVideos.tf_role),func.count(ytVideos.tf_role).label('count')]).group_by(ytVideos.tf_role).order_by(None)
    
    #f_role_count_query = q.statement.with_only_columns([(ytVideos.tf_role_combo),(ytVideos.tf_role_flank),(ytVideos.tf_role_offclass)]).group_by(ytVideos.tf_role).order_by(None)

    tf_role_subq = [func.count(getattr(ytVideos,f'tf_role_{tf_role}')).label(f'tf_class_{tf_role}') for tf_role in ['combo','flank','offclass']]
    tf_role_count_query = q.statement.with_only_columns(tf_role_subq).order_by(None)


    #class
    tf_classes =['scout','soldier', 'demo', 'medic', 'pyro', 'engineer', 'heavy', 'sniper', 'spy']
    tf_class_subq = [func.count(getattr(ytVideos,f'tf_class_{tf_class}')).label(f'tf_class_{tf_class}') for tf_class in tf_classes]
    tf_class_count_query = q.statement.with_only_columns(tf_class_subq).order_by(None)
    

    tf_map_full_result = list(q.session.execute(tf_map_full_count_query))

    tf_match_format_result = list(q.session.execute(tf_match_format_count_query))
    tf_resource_type_result = list(q.session.execute(tf_resource_type_count_query))
    tf_role_result = zip(("Combo/Pocket","Roamer/Flank","Offclass"),('combo','flank','offclass'),list(q.session.execute(tf_role_count_query))[0])
    print(tf_role_result)
    tf_class_result = list(q.session.execute(tf_class_count_query))[0]
    tf_class_result = list(zip(tf_classes,[x.capitalize() for x in tf_classes],tf_class_result))

    tf_map_full_result_dict = {}
    tf_match_format_result_dict = {}
    tf_role_result_dict = {}
    tf_resource_type_dict = {}
    tf_class_result_dict = {}

    for k,v in tf_resource_type_result:
        tf_resource_type_dict[k] = {'label':k,'value':k.lower(), 'count':v}

    for k,v in tf_match_format_result:
        tf_match_format_result_dict[k] = {'label':k,'value':k, 'count':v}

    for l,v,c in tf_role_result:
        
        tf_role_result_dict[v] = {'label':l,'value':v, 'count':c}

    for v,c in tf_map_full_result:
        l = ''
        try:
             #this label exists in the tf_versions database, but it should be fine to just take the element in the version after cp_ or koth_ or pl_ as the map label (name)
            l = v.split('_')[1].capitalize()
        except:
            continue
        
        tf_map_full_result_dict[l] = {'label':l,'value':v, 'count':c}

    for v,l,c in tf_class_result:
        tf_class_result_dict[v] = {'label':l,'value':v, 'count':c}

    
    for v,l,c in tf_class_result:
        tf_class_result_dict[v] = {'label':l,'value':v, 'count':c}

    print(tf_class_result_dict)
    return {"tf_map_full":tf_map_full_result_dict,"tf_match_format":tf_match_format_result_dict, "tf_role":tf_role_result_dict, "tf_resource_type":tf_resource_type_dict, "tf_class":tf_class_result_dict}


@views.route('/')
@views.route('/highlander')
@views.route('/sixes')
@views.route("/tf_map_select_get", methods = ['GET'])
def tf_map_select_get():

    #TODO update url parameters to real parameters
    arg_dic = request.args.to_dict(flat=False)
    try:
        tf_map_full = arg_dic['map']
    except: 
        tf_map_full = ['']
    try:
        creators = arg_dic['creators']
    except: 
        creators = ['']

    try:
        tf_classes = arg_dic['class']
    except: 
        tf_classes = ['']

    try:
        relevant_role = arg_dic['role']
        if len(relevant_role) == 1:
            relevant_role = relevant_role[0].split('&')
            

        if relevant_role == ['offclass']:
            tf_classes.extend(['Engineer', 'Sniper', 'Heavy', 'Spy', 'Pyro'])
            relevant_role = ['']
            print(tf_classes)
    except: 
        relevant_role = ['']

    try:
        resource_type = arg_dic['type']
    except: 
        resource_type = ['']
    try:
        within_date = arg_dic['date']
    except: 
        within_date = ['']
    try:
        id = arg_dic['id']
    except: 
        id = ['']
    try:
        language = arg_dic['language']
    except: 
        language = ['English']

    try:
        format = arg_dic['format']
    except: 
        format = ['']

    if creators == ['']:
        creators = None
    if resource_type == ['']:
        resource_type = None
    if tf_map_full == ['']:
        tf_map_full = None
    if tf_classes == ['']:
        tf_classes = None
    if relevant_role == ['']:
        relevant_role = None

    if within_date == ['']:
        within_date = None
    if id == ['']:
        id = None
    if format == ['']:
        format = None





    #construct filter
    tf_class_filter_dic = {'scout':ytVideos.tf_class_scout.isnot(None),'soldier':ytVideos.tf_class_soldier.isnot(None), 'demo':ytVideos.tf_class_demo.isnot(None), 'medic':ytVideos.tf_class_medic.isnot(None), 'pyro':ytVideos.tf_class_pyro.isnot(None), 'engineer':ytVideos.tf_class_engineer.isnot(None), 'heavy':ytVideos.tf_class_heavy.isnot(None), 'sniper':ytVideos.tf_class_sniper.isnot(None), 'spy':ytVideos.tf_class_spy.isnot(None)}
    tf_role_filter_dic = {'roamer':ytVideos.tf_role_flank.isnot(None),'flank':ytVideos.tf_role_flank.isnot(None), 'combo':ytVideos.tf_role_combo.isnot(None), 'pocket':ytVideos.tf_role_combo.isnot(None), 'offclass':ytVideos.tf_role_offclass.isnot(None)}

    query_filter = []
    query_class_filter = [] #can contain multiple classes which will be filtered using or_ in the SQLAlchemy query
    if tf_map_full:
        query_filter.append(ytVideos.tf_map_full.in_(tf_map_full))
    
    if creators:
        query_filter.append(or_(ytVideos.mrtf_display_id.in_(creators),ytVideos.st_creator_id.in_(creators),ytVideos.st_presenter_id.in_(creators)))
    
    if tf_classes:
        for tf_class in tf_classes:
            print("filtering ",tf_class)
            try:
                query_class_filter.append(tf_class_filter_dic[tf_class.lower()])
            except KeyError:
                print("Incorrect class filter: ", tf_class.lower())
    
    if relevant_role:
        for role in relevant_role:
            query_filter.append(tf_role_filter_dic[role])
            #query_filter.append(ytVideos.tf_role.in_(relevant_role)) #old

    if resource_type:
        query_filter.append(ytVideos.tf_resource_type.in_(resource_type))
    if within_date:
        print("within_date: ",within_date)
    if id:
        query_filter.append(ytVideos.yt_video_id.in_(id))
    
    if format:
        query_filter.append(ytVideos.tf_match_format.in_(format))

    query_filter.append(ytVideos.mrtf_language.in_(language))

    current_videos = db.session.query(ytVideos).order_by(ytVideos.yt_date_uploaded.desc()).filter(and_(or_(*query_class_filter),*query_filter))

    counts = get_yt_video_counts(current_videos)

    #print("counts: ", counts)
    print(and_(or_(*query_class_filter),*query_filter))
    vids = list(current_videos)
    results = {}
    for _vid in vids:
        yt_video_id = _vid.yt_video_id
        _vid = _vid.__dict__
        del _vid['_sa_instance_state']#remove sa object from dictionary to jsonify easier
        results[yt_video_id] = _vid
    
    results = sorted(list(results.values()), key=lambda d: d['mrtf_rating_score_a1'],reverse=True)

    #print('results ',results)
    #print('counts ',counts)
    
    #get votes if video is selected

    results_dict = {'results':results,'counts':counts}

    if id:
        

        results_dict['votes'] = get_user_vote(yt_video_id)


    return json.dumps(results_dict, default=str), 200


def get_user_vote(mrtf_item_id = None):
    _positive_votes = mrtfVotes.query.filter(and_(mrtfVotes.mrtf_item_id == mrtf_item_id ,mrtfVotes.mrtf_vote > 0)).with_entities(func.sum(mrtfVotes.mrtf_vote)).scalar()
    print(_positive_votes)
    _negative_votes = mrtfVotes.query.filter(and_(mrtfVotes.mrtf_item_id == mrtf_item_id ,mrtfVotes.mrtf_vote < 0)).with_entities(func.sum(mrtfVotes.mrtf_vote)).scalar()
    print(_negative_votes)

    _positive_votes = 0 if _positive_votes == None else _positive_votes
    _negative_votes = 0 if _negative_votes == None else _negative_votes
    try:
        session['st_id3']
    except:
        #must be logged in
        return {'up':int(_positive_votes),'down':int(_negative_votes),'total':int(_positive_votes)+int(_negative_votes),'user':'none'}

    _votes = mrtfVotes.query.filter(and_(mrtfVotes.mrtf_item_id == mrtf_item_id ,mrtfVotes.mrtf_user_st_id3 == session['st_id3'],mrtfVotes.mrtf_vote !=0))
    print(_votes)
    if _votes.count() > 0:
        #youve voted, 
        _vote = _votes.one()
        if _vote.mrtf_vote > 0: 
            _vote_updown = "up"
        elif _vote.mrtf_vote < 0:
            _vote_updown = "down"
        
    else:
        #you havent voted
        _vote_updown = 'none'
        
    return {'up':int(_positive_votes),'down':int(_negative_votes), 'total':int(_positive_votes)+int(_negative_votes),'user':_vote_updown}



@views.route("/query_yt_clips", methods = ['GET'])
def query_yt_clips():
    arg_dic = request.args.to_dict(flat=False)
    try:
        tf_map_full = arg_dic['map']
    except: 
        tf_map_full = ['']
    try:
        creators = arg_dic['creators']
    except: 
        creators = ['']

    try:
        tf_classes = arg_dic['class']
    except: 
        tf_classes = ['']

    try:
        relevant_role = arg_dic['role']
    except: 
        relevant_role = ['']

    try:
        resource_type = arg_dic['type']
    except: 
        resource_type = ['']
    try:
        within_date = arg_dic['date']
    except: 
        within_date = ['']
    try:
        id = arg_dic['id']
    except: 
        id = ['']
    try:
        clip_id = arg_dic['clip_id']
    except: 
        clip_id = ['']

    if creators == ['']:
        creators = None
    if resource_type == ['']:
        resource_type = None
    if tf_map_full == ['']:
        tf_map_full = None
    if tf_classes == ['']:
        tf_classes = None
    if relevant_role == ['']:
        relevant_role = None

    if within_date == ['']:
        within_date = None
    if id == ['']:
        id = None
    if clip_id == ['']:
        clip_id = None

    #construct filter

    tf_class_filter_dic ={'scout':ytClips.tf_class_scout.isnot(None),'soldier':ytClips.tf_class_soldier.isnot(None), 'demo':ytClips.tf_class_demo.isnot(None), 'medic':ytClips.tf_class_medic.isnot(None), 'pyro':ytClips.tf_class_pyro.isnot(None), 'engineer':ytClips.tf_class_engineer.isnot(None), 'heavy':ytClips.tf_class_heavy.isnot(None), 'sniper':ytClips.tf_class_sniper.isnot(None), 'spy':ytClips.tf_class_spy.isnot(None)}
    
    clip_query_filter = []
    if tf_map_full:
        clip_query_filter.append(ytClips.tf_map_full.in_(tf_map_full))
    #TODO fix this
    #if creators:
    #    clip_query_filter.append(ytClips.st_presenter_id.in_(creators))
    if tf_classes:
        for tf_class in tf_classes:
            try:
                clip_query_filter.append(tf_class_filter_dic[tf_class.lower()])
            except KeyError:
                print("Incorrect class filter: ", tf_class)
    if relevant_role:
        clip_query_filter.append(ytClips.tf_role.in_(relevant_role))
    if resource_type:
        clip_query_filter.append(ytClips.tf_resource_type.in_(resource_type))
    if within_date:
        print("within_date: ",within_date)
    if clip_id:
        clip_query_filter.append(ytClips.yt_video_id.in_(id))
    
    current_clips = db.session.query(ytClips).filter(*clip_query_filter)
    clips = list(current_clips)
    clip_results = {}
    for _cli in clips:
        yt_clip_id = _cli.yt_clip_id
        _cli = _cli.__dict__
        del _cli['_sa_instance_state']#remove sa object from dictionary to jsonify easier
        clip_results[yt_clip_id] = _cli


    return clip_results, 200


    


@views.route('/fetch_videos', methods=['GET'])
def fetch_videos():
    print("fetch_videos")
    _videos = ytVideos.query.all()
    _versions = list(set(db.session.execute(db.select(tfVersions.tf_map_full, tfVersions.tf_map_name))))
    _creators = list(set(db.session.execute(db.select(ytVideos.mrtf_display_name,ytVideos.mrtf_display_id))))
    print([_vid.yt_stats_likes for _vid in _videos])
    return render_template("./fetch_videos.html",videos=_videos,creators=_creators,versions=_versions)


@views.route('/about', methods=['POST','GET'])
def about():
    title_text = "TF2 Map Review - About"
    return render_template("./about.html",title_text=title_text)


@views.route('/feedback')
def feedback():
    title_text = "TF2 Map Review - Feeback"
    return render_template("./feedback_form.html",title_text=title_text)

@views.route('/privacy_policy')
def privacy_policy():
    title_text = "TF2 Map Review - Privacy Policy"
    return render_template("./privacy_policy.html",title_text=title_text)

@views.route('/populate_yt_stats', methods=['POST'])
def yt_stats():
    yt_video_id = request.form['yt_video_id']
    print(yt_video_id)
    search_url = "https://www.googleapis.com/youtube/v3/videos"
    search_params = {
        'key': current_app.config["YOUTUBE_API_KEY"],
        'part':"snippet,statistics",
        "id":yt_video_id
    }
    r = requests.get(search_url,search_params)
    
    return r.json()
    
def get_yt_channel_image(yt_channel_id):
    search_url = "https://www.googleapis.com/youtube/v3/channels"
    search_params = {
        'key': current_app.config["YOUTUBE_API_KEY"],
        'part':"snippet",
        "id":yt_channel_id}
    r = requests.get(search_url,search_params)
    return r.json()["items"][0]["snippet"]["thumbnails"]["default"]["url"]



def is_yt_video_id_valid(yt_video_id):
    '''Check with YouTube v3 API if yt_video_id is valid. Return {'count':1} if it is else {'count':0} if it isnt'''
    search_url = "https://www.googleapis.com/youtube/v3/videos"
    search_params = {'key': current_app.config["YOUTUBE_API_KEY"],'part':"snippet","id":yt_video_id}
    r = requests.get(search_url,search_params)
    return True if r.json()['pageInfo']['totalResults'] == 1 else False
    
def is_yt_video_id_in_database(yt_video_id):
    _videos = db.session.query(ytVideos).filter(ytVideos.yt_video_id.in_([yt_video_id]))
    return True if len(list(_videos)) > 0 else False
    


@views.route('/yt_channel_id_lookup', methods=['GET'])
def yt_channel_id_lookup():
    arg_dic = request.args.to_dict(flat=False)
    yt_channel_id = arg_dic['yt_channel_id'][0]
    
    yt_channel_image = get_yt_channel_image(yt_channel_id)
    _videos = db.session.query(ytVideos).filter(ytVideos.yt_channel_id.in_([yt_channel_id]))
    vids = list(_videos)
    results = {}
    print(len(vids))
    if len(vids) > 0:
        for _vid in vids:
            yt_channel_id = _vid.yt_channel_id
            _vid = _vid.__dict__
            del _vid['_sa_instance_state']#remove sa object from dictionary to jsonify easier
            
            results[yt_channel_id] = _vid
    else:
        print("yt_channel_id ",yt_channel_id)
        results[yt_channel_id] = {}

    results[yt_channel_id]['yt_channel_image'] = yt_channel_image
    return jsonify(results), 200



@views.route('/check_existing_videos', methods=['GET'])
def check_existing_videos():
    arg_dic = request.args.to_dict(flat=False)
    yt_video_id = arg_dic['yt_video_id']
    _videos = db.session.query(ytVideos).filter(ytVideos.yt_video_id.in_(yt_video_id))
    vids = len(list(_videos))
    return jsonify(vids), 200



@views.route('/temporary', methods=['GET'])
def temporary():
    return render_template('./temporary.html')
    yt_video_id = arg_dic['yt_video_id']


@views.route('/submit_vote', methods=['POST'])
def submit_vote():
    try:
        session['st_id3']
    except:
        return "You must be logged in to vote", 401
    
    _vote_updown = request.form['vote']
    if _vote_updown == "up":
        vote_sign = 1 
    elif _vote_updown == "down":
        vote_sign = -1
    args = dict(parse_qsl(urlparse(request.referrer).query))
    mrtf_item_id = args['id']
    _votes = mrtfVotes.query.filter(and_(mrtfVotes.mrtf_item_id == mrtf_item_id ,mrtfVotes.mrtf_user_st_id3 == session['st_id3'],mrtfVotes.mrtf_vote !=0))
    #_votes = list(_votes)
    print(_votes.count())
    try:
        vote_power = session['vote_power']
    except:
        vote_power = 1
    
    if _votes.count() == 0:
        #you have not voted here before add vote
        vote_dict = {'mrtf_item_id': mrtf_item_id,
            'mrtf_user_st_id3': session['st_id3'],
            'mrtf_vote':vote_sign*vote_power,
            'mrtf_datetime_voted':datetime.now()}
        _vote = mrtfVotes()
        for k,v in vote_dict.items():
            setattr(_vote,k,v)

        try:
            setattr(_vote,"mrtf_vote_ip",str(request.headers.get('X-Forwarded-For')))
        except:
            pass
        
        db.session.add(_vote)
        db.session.commit()


    elif _votes.count() == 1:
        print('lenght of 1')
        #you have voted here before change vote
        
        _vote = _votes.one()
        if (_vote.mrtf_vote > 0 and vote_sign > 0) or (_vote.mrtf_vote < 0 and vote_sign < 0):
            #clicked on existing vote, remove vote object
            db.session.delete(_vote)
            db.session.commit()
        else:
            #clicked on opposite vote, change sign of vote object
            _vote.mrtf_vote = _vote.mrtf_vote * -1
            db.session.commit()
    else:
        print('lenght of unknown?')
        pass
        #another error?

    #print(list(_votes)[0][0])
    #have you voted on this before?

    
    #return user vote dict
    return get_user_vote(mrtf_item_id), 200

    


@views.route('/get_votes', methods=['POST'])
def get_votes(mrtf_item_id=None):

    #get all votes fro current item
    _votes = db.session.execute(db.session.query(mrtfVotes).filter(mrtfVotes.mrtf_item_id.in_(mrtf_item_id)))
    print(_votes)
    #check if logged in
    if session['st_id3']:
        #is logged in
        print(session['st_id3'])



    #user = session.st
    #_user_st_id3 = None
    #_user_vote = None
    
    #I want to know, if a user has voted on the item, so get the users record
    #I also want to sum all of the mrtf_votes for the video
    #I also want to get all unique mrtf_tags that are not provisional and their counts
    return

@views.route('/get_chapters', methods=['GET'])
def get_chapters(yt_video_id=None):
    print('getting chapters for ', yt_video_id)
    if not yt_video_id:
        arg_dic = request.args.to_dict(flat=False)
        yt_video_id = arg_dic['yt_video_id']

    _chapters = db.session.execute(db.session.query(ytChapters).filter(ytChapters.yt_video_id.in_(yt_video_id)).order_by(ytChapters.yt_chapter_start))
    _chapters = [_c[0] for _c in list(_chapters)]
    #print(_chapters)
    if len(_chapters) == 0:
        return jsonify([]), 204
    else:
        return jsonify(_chapters), 200



# Return validation errors as JSON
@views.errorhandler(422)
@views.errorhandler(400)
def handle_error(err):
    
    headers = err.data.get("headers", None)
    messages = err.data.get("messages", ["Invalid request."])
    if headers:
        
        return jsonify({"errors": messages}), err.code, headers
    else:
        return jsonify({"errors": messages}), err.code
    

@views.route('/get_mrtf_hacker_tracker',methods=['GET'])
def get_mrtf_hacker_tracker():
    #query_filter.append(ytVideos.mrtf_language.in_(language))
    return


def tesssst():
    #steampai use
    # get playtime
    api_key = current_app.config["STEAM_API_KEY"]
    st_id64 = '76561198982713227'
    f'https://api.steampowered.com/IPlayerService/GetRecentlyPlayedGames/v1/?key={api_key}&steamid={st_id64}&appid=440'

    # summary
    st_id64_string = '76561198982713227' #comma separated list up to 100 values
    f'https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v2/?key={api_key}&steamids={st_id64_string}&appid=440'
    
@views.route('/ht', methods=['GET'])
def hacker_tracker():
    _hackers  = mrtfHackerTracker.query.all()
    #print([x[0] for x in list(_hackers)])
    print(_hackers)
    return render_template('./hacker_tracker.html',hackers =_hackers)


@views.route('/cheaters', methods=['GET'])
def show_cheaters():
    return send_from_directory('static/txt/','cheaters.txt')
