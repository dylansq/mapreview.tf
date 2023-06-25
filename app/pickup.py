from flask import Blueprint, render_template, request, flash, url_for, jsonify,redirect, current_app, send_from_directory
from flask_cors import CORS
from .models import ptfServers
from . import db
import json
from urllib.parse import urlencode
import requests
import git
from datetime import datetime, timezone
from dateutil import parser as dtparser
import pytz
import urllib.parse
import operator

#SQLAlchemy
from sqlalchemy import or_, and_
from sqlalchemy import func, distinct
from sqlalchemy.orm import lazyload
from sqlalchemy.sql import label

#Sessions
from flask_session import Session
from flask import session

#Webargs Validation
from webargs import fields, validate
from webargs.flaskparser import parser
from webargs.flaskparser import abort

#Initialize Blueprints
pickup = Blueprint("pickup", __name__)

#Setup CORS for pickup
CORS(pickup)

#Routes
#Housekeeping
@pickup.route('/robots.txt')
def static_from_root():
    '''Return static text documents'''
    return send_from_directory('static/txt/', request.path[1:])

@pickup.route('/webhook', methods=['POST'])
def webhook():
    '''Github Webhook for autoupdating server repo'''
    if request.method == 'POST':
        print(request) 
        repo = git.Repo('./pickup.tf')
        repo.git.reset('--hard')
        origin = repo.remotes.origin
        origin.pull()
        return '', 200
    else:
        return ''
    
#Testing

#External
def get_ip_geolocation(ipv4,parameter = None):
    #Check database for cached ip/country_code
    #TODO:// 
    #No cache found, get data from:
    search_url = 'https://api.ipgeolocation.io/ipgeo'
    search_params = {
        'apiKey': current_app.config["IPGEOLOCATION_API_KEY"],
        'ip': ipv4 }
    r = requests.get(search_url,search_params)

    #['ip', 'continent_code', 'continent_name', 'country_code2', 'country_code3', 'country_name','state_prov', 'languages': 'en-US,es-US,haw,fr', 'time_zone']

    #Add record to database
    try:
        if parameter:
            return r.json()['parameter']
        else:
            return r.json()
    except:
        return None
    
#Main Routes
@pickup.route('/',methods=['GET','POST'])
def browse():
    #ptf_servers = list(set(db.session.execute(db.select(ptfServers.ptf_server_name,ptfServers.ptf_server_status).order_by(ptfServers.ptf_server_status))))
    ptf_servers = list(db.session.query(ptfServers).order_by(ptfServers.ptf_server_status.asc()).filter(ptfServers.ptf_server_status.not_in(['9'])))
    results = {}
    for _server in ptf_servers:
        ptf_server_id = _server.ptf_server_id
        _server = _server.__dict__
        del _server['_sa_instance_state']#remove sa object from dictionary to jsonify easier
        results[ptf_server_id] = _server
    
    results = sorted(list(results.values()), key=lambda d: d['ptf_server_status'])
    meta_dic = {"description":"testing"}
    status_dic = {1:["Active",'active'], 2:["Inactive",'inactive'], 3:["In-Development",'dev'],7:["Other",'other'],8:["Unknown",'unknown'], 9:["Dead",'dead'], 0:["All",'all']}
    return render_template("main.html",ptf_servers=results,meta_dic=meta_dic,status_dic=status_dic)

@pickup.route('/update_listings/',methods=['GET'])
def update_listings():
    arg_dic = request.args.to_dict(flat=False)
    print(arg_dic)
    #Update this if more search parameters are added
    args_dic = {'language':[''],'region':[''],'gamemode':[''],'gametype':[''],'status':[''],'skill':['']}
    arg_labels =  ['language','region','gamemode','gametype','status','skill']
    for arg in args_dic.keys():
        try:
            if '+' in arg_dic[arg][0]:
                args_dic[arg] = arg_dic[arg][0].split('+')
            else:
                args_dic[arg] = arg_dic[arg]
        except:
            #argument not found in arg_dic
            continue
    print(args_dic['skill'])
    #Construct filters
    ptf_language_filter = ''
    ptf_region_filter_dic = {'na':ptfServers.ptf_region_na.isnot(None),'sa':ptfServers.ptf_region_sa.isnot(None),'eu':ptfServers.ptf_region_eu.isnot(None),'as':ptfServers.ptf_region_as.isnot(None),'oc':ptfServers.ptf_region_oc.isnot(None),'af':ptfServers.ptf_region_af.isnot(None)}
    tf_skill_filter_dic = {'0':ptfServers.tf_skilllevel_0.isnot(None),'1':ptfServers.tf_skilllevel_1.isnot(None),'2':ptfServers.tf_skilllevel_2.isnot(None),'3':ptfServers.tf_skilllevel_3.isnot(None)}
    ptf_gamemode_filter_dic = {'ultiduo':ptfServers.tf_gamemode_ultiduo.isnot(None),'ultitrio':ptfServers.tf_gamemode_ultitrio.isnot(None),'fours':ptfServers.tf_gamemode_fours.isnot(None),'sixes':ptfServers.tf_gamemode_sixes.isnot(None),'prolander':ptfServers.tf_gamemode_prolander.isnot(None),'highlander':ptfServers.tf_gamemode_highlander.isnot(None)}
    ptf_gametype_filter_dic ={'experimental':ptfServers.tf_gamemode_experimental.isnot(None),'passtime':ptfServers.tf_gamemode_passtime.isnot(None),'bball':ptfServers.tf_gamemode_bball.isnot(None),'mge':ptfServers.tf_gamemode_mge.isnot(None),'mvm':ptfServers.tf_gamemode_mvm.isnot(None)}

    #TODO handel other
    #,'other':ptfServers.tf_gamemode_other.isnot(None)

    query_filter = []
    #query_filter_or = [] #can contain multiple classes which will be filtered using or_ in the SQLAlchemy query

    #print([tf_skill_filter_dic[_var] for _var in [skill]])
    if args_dic['language'][0]:
        query_filter.append(ptfServers.ptf_language.in_(args_dic['language']))
    if args_dic['region'][0]:
        query_filter.extend([ptf_region_filter_dic[_var] for _var in args_dic['region']])
    if args_dic['gamemode'][0]:
        query_filter.extend([ptf_gamemode_filter_dic[_var] for _var in args_dic['gamemode']])
    if args_dic['gametype'][0]:
        query_filter.extend([ptf_gametype_filter_dic[_var] for _var in args_dic['gametype']])
    if args_dic['status'][0]:
        query_filter.append(ptfServers.ptf_server_status.in_(args_dic['status']))
    if args_dic['skill'][0]:
        _qf = [tf_skill_filter_dic[_var] for _var in args_dic['skill']]
        
        query_filter.extend(or_(*_qf)) if len(_qf) > 1 else query_filter.extend(_qf)
        print(query_filter)

    listings = db.session.query(ptfServers).filter(and_(*query_filter))
    counts = get_yt_video_counts(listings.filter(ptfServers.ptf_server_status.in_([1,2,3,4,5,6,7])))#remove 8,9, unknown and dead
    results = {}
    for _li in list(listings):
        ptf_server_id = _li.ptf_server_id
        _li = _li.__dict__
        del _li['_sa_instance_state']#remove sa object from dictionary to jsonify easier
        results[ptf_server_id] = _li
    
    #results = sorted(list(results.values()), key=lambda d: d['mrtf_rating_score_a1'],reverse=True)
    return json.dumps({'results':results,'counts':counts}, default=str), 200

def get_yt_video_counts(q):    
    ptf_regions = ['na','sa','eu','as','oc','af']
    tf_gamemodes = ['ultiduo','ultitrio','fours','sixes','prolander','highlander']
    tf_gametypes = ['bball','passtime','experimental','mge','mvm']
    tf_skilllevels = ['0','1','2','3']

    ptf_region_subq = [func.count(getattr(ptfServers,f'ptf_region_{region_code}')).label(f'ptf_region_{region_code}') for region_code in ptf_regions]
    tf_gamemode_subq = [func.count(getattr(ptfServers,f'tf_gamemode_{gamemode}')).label(f'tf_gamemode_{gamemode}') for gamemode in tf_gamemodes]
    tf_gametype_subq = [func.count(getattr(ptfServers,f'tf_gamemode_{gametypes}')).label(f'tf_gamemode_{gametypes}') for gametypes in tf_gametypes]
    tf_skilllevel_subq = [func.count(getattr(ptfServers,f'tf_skilllevel_{skilllevel}')).label(f'tf_skilllevel_{skilllevel}') for skilllevel in tf_skilllevels]
    
    ptf_language_countquery = q.statement.with_only_columns([(ptfServers.ptf_language),func.count(ptfServers.ptf_language).label('count')]).group_by(ptfServers.ptf_language).order_by(None)
    ptf_server_status_countquery = q.statement.with_only_columns([(ptfServers.ptf_server_status),func.count(ptfServers.ptf_server_status).label('count')]).group_by(ptfServers.ptf_server_status).order_by(None)
    ptf_region_countquery = q.statement.with_only_columns(ptf_region_subq).order_by(None)
    tf_gamemode_countquery = q.statement.with_only_columns(tf_gamemode_subq).order_by(None)
    tf_gametype_countquery = q.statement.with_only_columns(tf_gametype_subq).order_by(None)
    tf_skilllevel_countquery = q.statement.with_only_columns(tf_skilllevel_subq).order_by(None)

    ptf_language_result = list(q.session.execute(ptf_language_countquery))
    ptf_server_status_result = list(q.session.execute(ptf_server_status_countquery))
    ptf_region_result = list(q.session.execute(ptf_region_countquery))
    tf_gamemode_result = list(q.session.execute(tf_gamemode_countquery))
    tf_gametype_result = list(q.session.execute(tf_gametype_countquery))
    tf_skilllevel_result = list(q.session.execute(tf_skilllevel_countquery))

    ptf_language_result_dict = {}
    ptf_server_status_result_dict = {}
    ptf_region_result_dict = {}
    tf_gamemode_result_dict = {}
    tf_gametype_result_dict = {}
    tf_skilllevel_result_dict = {}
    for k,c in ptf_language_result:
        if not k:
            continue #None showing up in k
        ptf_language_result_dict[k] = {'label':k,'value':k, 'count':c}

    for k,c in ptf_server_status_result:
        status_dic = {1:["Active",'active'], 2:["Inactive",'inactive'], 3:["In-Development",'dev'],7:["Other",'other'],8:["Unknown",'unknown'], 9:["Dead",'dead'], 0:["All",'all']}
        ptf_server_status_result_dict[str(k)] = {'label':status_dic[int(k)][0],'value':str(k), 'count':c}
    
    for k,c in zip(ptf_regions,ptf_region_result[0]):
        ptf_region_result_dict[k] = {'label':k,'value':k, 'count':c}
    
    for k,c in zip(tf_gamemodes,tf_gamemode_result[0]):
        tf_gamemode_result_dict[k] = {'label':k,'value':k, 'count':c}
    
    for k,c in zip(tf_gametypes,tf_gametype_result[0]):
        tf_gametype_result_dict[k] = {'label':k,'value':k, 'count':c}
    
    for k,l,c in zip(tf_skilllevels,['New Players','Open (NC/AM)','Mid (IM/Main)','High (Adv+)'],tf_skilllevel_result[0]):
        tf_skilllevel_result_dict[k] = {'label':l,'value':k, 'count':c}

    return {"language":ptf_language_result_dict,"status":ptf_server_status_result_dict, "region":ptf_region_result_dict, "gamemode":tf_gamemode_result_dict, "gametype":tf_gametype_result_dict, "skill":tf_skilllevel_result_dict}

