from flask import Blueprint, render_template, request, flash, url_for, jsonify,redirect, current_app, send_from_directory
from flask_cors import CORS
from .models import ptfServers, ptfUsers, ptfChannels
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
import math

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
from webargs.flaskparser import parser, abort, use_args
#from webargs.fields import DelimitedList
from marshmallow import Schema, EXCLUDE, pre_load

from .external import steam_query

#Initialize Blueprints
pickup = Blueprint("pickup", __name__)



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


#Main Routes
@pickup.route('/admin',methods=['GET','POST'])
def admin_pannel():
    try:
        session['st_id3']
    except:
        print('fail')
        return "You must be logged in to vote", 401
    
    user = list(db.session.query(ptfUsers).filter(and_((ptfUsers.st_id64 == session['st_id64']),or_(ptfUsers.ptf_server_role_owner.isnot(False),ptfUsers.ptf_server_role_admin.isnot(False),ptfUsers.ptf_server_role_developer.isnot(False)))))
    print(session['st_id64'],user)
    server_ids = [str(server.ptf_server_id) for server in user]
    is_developer = any([server.ptf_server_role_developer for server in user])
    print('is_developer: ', is_developer)
    #ptf_servers = list(set(db.session.execute(db.select(ptfServers.ptf_server_name,ptfServers.ptf_server_status).order_by(ptfServers.ptf_server_status))))
    if is_developer:
        ptf_servers = list(db.session.query(ptfServers))
    else:
        ptf_servers = list(db.session.query(ptfServers).filter(ptfServers.ptf_server_id.in_(server_ids)))
    results = {}
    for _server in ptf_servers:
        ptf_server_id = _server.ptf_server_id
        _server = _server.__dict__
        del _server['_sa_instance_state']#remove sa object from dictionary to jsonify easier
        del _server['ptf_modified_ip']
        del _server['ptf_modified_steamid64']
        del _server['ptf_upload_ip']
        del _server['ptf_datetime_modified']
        results[ptf_server_id] = _server
    
    if is_developer:
        ptf_users = list(db.session.query(ptfUsers))
    else:
        ptf_users = list(db.session.query(ptfUsers).filter(ptfUsers.ptf_server_id.in_(server_ids)))

    user_results = {}
    user_id_list = []
    for _user in ptf_users:
        ptf_users_key = _user.ptf_users_key
        _user = _user.__dict__
        del _user['_sa_instance_state']#remove sa object from dictionary to jsonify easier
        user_id_list.append(_user['st_id64'])
        #get steam avatars

        try:
            user_results[_user['ptf_server_id']].append(_user)
        except:
            user_results[_user['ptf_server_id']] = [_user]

    
    #query all steam users at once
    
    _sq = {}
    unique_st_id64 = list(set(user_id_list))
    id_count = len(unique_st_id64)
    #can handel max of 100 ids per request
    for i in range(math.ceil(id_count/100)):
        user_id_string = ','.join(unique_st_id64[i*100:(i+1)*100])
        __sq = steam_query(user_id_string)
        if __sq[1] == 200:
            _sq.update(__sq[0])
    
    print(_sq)
    for ptf_server_id in user_results.keys():
        #loop over each server
        for i, _user in enumerate(user_results[ptf_server_id]):
            #loop over each user in a server
            user_results[ptf_server_id][i]['st_display_avatar'] = _sq[_user['st_id64']]['avatar']
            
            #user_results[_server][i]['st_display_name'] = _sq[0][_user['st_id64']]['personaname']


        
    #results = sorted(list(results.values()), key=lambda d: d['ptf_server_status'])
    meta_dic = {"description":"testing"}
    status_dic = {1:["Active",'active'], 2:["Inactive",'inactive'], 3:["In-Development",'dev'],7:["Other",'other'],8:["Unknown",'unknown'], 9:["Dead",'dead'], 0:["All",'all']}
    return render_template("pickup/pickup_admin.html",ptf_servers=results,ptf_users=user_results,meta_dic=meta_dic,status_dic=status_dic)





@pickup.route('/update_listings/',methods=['GET'])
def update_listings():
    arg_dic = request.args.to_dict(flat=False)
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
    #Construct filters
    ptf_language_filter = ''
    ptf_region_filter_dic = {'na':ptfServers.ptf_region_na.isnot(False),'sa':ptfServers.ptf_region_sa.isnot(False),'eu':ptfServers.ptf_region_eu.isnot(False),'as':ptfServers.ptf_region_as.isnot(False),'oc':ptfServers.ptf_region_oc.isnot(False),'af':ptfServers.ptf_region_af.isnot(False)}
    tf_skill_filter_dic = {'0':ptfServers.tf_skilllevel_0.isnot(False),'1':ptfServers.tf_skilllevel_1.isnot(False),'2':ptfServers.tf_skilllevel_2.isnot(False),'3':ptfServers.tf_skilllevel_3.isnot(False)}
    ptf_gamemode_filter_dic = {'ultiduo':ptfServers.tf_gamemode_ultiduo.isnot(False),'ultitrio':ptfServers.tf_gamemode_ultitrio.isnot(False),'fours':ptfServers.tf_gamemode_fours.isnot(False),'sixes':ptfServers.tf_gamemode_sixes.isnot(False),'prolander':ptfServers.tf_gamemode_prolander.isnot(False),'highlander':ptfServers.tf_gamemode_highlander.isnot(False)}
    ptf_gametype_filter_dic ={'experimental':ptfServers.tf_gamemode_experimental.isnot(False),'passtime':ptfServers.tf_gamemode_passtime.isnot(False),'bball':ptfServers.tf_gamemode_bball.isnot(False),'mge':ptfServers.tf_gamemode_mge.isnot(False),'mvm':ptfServers.tf_gamemode_mvm.isnot(False)}

    #TODO handel other
    #,'other':ptfServers.tf_gamemode_other.isnot(None)

    query_filter = []
    #query_filter_or = [] #can contain multiple classes which will be filtered using or_ in the SQLAlchemy query

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

    channels = db.session.query(ptfChannels)
    channels_dict = {}
    for _ch in list(channels):
        try:
            channels_dict[_ch.ptf_server_id].append(_ch.__dict__)
        except:
            channels_dict[_ch.ptf_server_id] = [_ch.__dict__]
    listings = db.session.query(ptfServers).filter(and_(*query_filter))
    counts = get_yt_video_counts(listings.filter(ptfServers.ptf_server_status.in_([1,2,3,4,5,6,7])))#remove 8,9, unknown and dead


    results = {}
    for _li in list(listings):
        ptf_server_id = _li.ptf_server_id
        _li = _li.__dict__
        #if the server isn't tracked, return -1
        _li_playing = -1
        _li_waiting = -1
        _li_spectating = -1
        if str(ptf_server_id) in channels_dict.keys():
            _li_playing = 0
            _li_waiting = 0
            _li_spectating = 0
            for _ch in channels_dict[str(ptf_server_id)]:
                try:
                    _li_playing += int(_ch['ptf_playing'])
                    _li_waiting += int(_ch['ptf_waiting'])
                    _li_spectating += int(_ch['ptf_spectating'])
                except:
                    pass

        #add active playing/waiting/spectating counts:
        _li['ptf_playing'] = _li_playing
        _li['ptf_waiting'] = _li_waiting
        _li['ptf_spectating'] = _li_spectating

        #remove sa object from dictionary to jsonify easier
        del _li['_sa_instance_state']

        #remove sensitive data
        del _li['ptf_upload_ip']
        del _li['ptf_upload_steamid64']
        del _li['ptf_datetime_modified']
        del _li['ptf_modified_ip']
        del _li['ptf_modified_steamid64']

        _li['ptf_owners'] = []
        _li['ptf_admins'] = []
        _li['ptf_moderators'] = []

        results[ptf_server_id] = _li

    
    for user in db.session.query(ptfUsers).all():
        user = user.__dict__
        ptf_server_id = user['ptf_server_id']
        if ptf_server_id in results.keys():
            #get owner/admin/mod - only add user to one category
            if user['ptf_server_role_owner']:
                roles = 'ptf_owners'
            elif user['ptf_server_role_admin']:
                roles = 'ptf_admins'
            elif user['ptf_server_role_moderator']:
                roles = 'ptf_moderators'
            else:
                #skip non owner/admin/mod roles
                continue
            
            
            user_role = {'st_display_name':user['st_display_name'],
                         'st_id64':user['st_id64'],
                         'st_display_avatar': user['st_avatar_url']}
            
            results[ptf_server_id][roles].append(user_role)


    response = jsonify({'results':results,'counts':counts})
    response.headers.add('Access-Control-Allow-Origin', '*') #allow cross origin in headder
    return response #json.dumps({'results':results,'counts':counts}, default=str), 200

#depreciated
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

@pickup.route("/steam_auth")
def auth_with_steam(origin=None):
    arg_dic = request.args.to_dict(flat=False)
    host = '://'.join(urllib.parse.urlparse(request.base_url)[:2])
    try:
        origin = 'origin='+ str(arg_dic['origin'][0])
    except:
        origin = "origin=https://pickup.tf"

    steam_openid_url = 'https://steamcommunity.com/openid/login'
    params = {
    'openid.ns': "http://specs.openid.net/auth/2.0",
    'openid.identity': "http://specs.openid.net/auth/2.0/identifier_select",
    'openid.claimed_id': "http://specs.openid.net/auth/2.0/identifier_select",
    'openid.mode': 'checkid_setup',
    'openid.return_to': f'{host}/ext/authorize?'+origin,
    'openid.realm': host
    }
    query_string = urlencode(params)
    auth_url = steam_openid_url + "?" + query_string
    #print(auth_url)
    return redirect(auth_url)


#CRUD opperations

# Return validation errors as JSON
@pickup.errorhandler(422)
@pickup.errorhandler(400)
def handle_error(err):
    headers = err.data.get("headers", None)
    messages = err.data.get("messages", ["Invalid request."])
    if headers:
        return jsonify({"errors": messages}), err.code, headers
    else:
        return jsonify({"errors": messages}), err.code


class ptfUpdateServer(Schema):
    ptf_server_id = fields.Int()
    ptf_steamcommunity_url = fields.URL(allow_none=True)
    ptf_discord_url = fields.URL(allow_none=True)
    ptf_site_url = fields.URL(allow_none=True)

    ptf_skill = fields.DelimitedList(fields.Str(allow_none=True), delimiter=',',allow_none=True)
    ptf_region = fields.DelimitedList(fields.Str(allow_none=True), delimiter=',',allow_none=True)
    ptf_gamemode = fields.DelimitedList(fields.Str(allow_none=True), delimiter=',',allow_none=True)
    ptf_gametype = fields.DelimitedList(fields.Str(allow_none=True), delimiter=',',allow_none=True)

    ptf_role_owner = fields.DelimitedList(fields.Str(allow_none=True), delimiter=',',allow_none=True)
    ptf_role_admin = fields.DelimitedList(fields.Str(allow_none=True), delimiter=',',allow_none=True)
    ptf_role_moderator = fields.DelimitedList(fields.Str(allow_none=True), delimiter=',',allow_none=True)

    ptf_server_name = fields.Str()
    ptf_server_description = fields.Str(allow_none=True)


    @pre_load
    def replace_empty_strings_with_nones(self, data, **kwargs):
        data = data.to_dict()
        for key in data.keys():
            if data[key] == "":
                data[key] = None
        return data
    
    class Meta:
        unknown = EXCLUDE




@pickup.route("/update_server",methods=['POST'])
@use_args(ptfUpdateServer(), location='form', unknown=None)
def update_server(args):
    '''Accept POST request for ptf_users submit'''
    print(f"args: {args}")
    try:
        session['st_id3']
    except:
        return "You must be logged in to update server data", 401
    
    ptf_server_id = args['ptf_server_id']
    
    #Recheck who submitter is and check if they can update the server data
    _submitter = db.session.query(ptfUsers).filter(and_(ptfUsers.st_id64 == session['st_id64'],ptfUsers.ptf_server_id == ptf_server_id)).first()
    if not _submitter:
       _submitter = db.session.query(ptfUsers).filter(and_(ptfUsers.st_id64 == session['st_id64'],ptfUsers.ptf_server_role_developer)).first()

    if _submitter.ptf_server_role_admin or _submitter.ptf_server_role_owner or _submitter.ptf_server_role_developer:
        pass
    else:
        return "You do not have permission to edit the data for this server", 401
    

    _server = db.session.query(ptfServers).filter(ptfServers.ptf_server_id == ptf_server_id).first()

    #print(args['ptf_server_description'])



    ptf_fields_dict = {'ptf_skill':['tf_skilllevel_0', 'tf_skilllevel_1', 'tf_skilllevel_2', 'tf_skilllevel_3'],
                       'ptf_gamemode':['tf_gamemode_ultiduo', 'tf_gamemode_ultitrio', 'tf_gamemode_fours', 'tf_gamemode_sixes', 'tf_gamemode_prolander', 'tf_gamemode_highlander'],
                       'ptf_gametype':['tf_gamemode_bball', 'tf_gamemode_passtime', 'tf_gamemode_experimental', 'tf_gamemode_mge', 'tf_gamemode_mvm'],
                       'ptf_region':['ptf_region_na', 'ptf_region_sa',  'ptf_region_eu', 'ptf_region_af', 'ptf_region_as', 'ptf_region_oc']}

    
    for ptf_field_key, ptf_fields in ptf_fields_dict.items():
        for ptf_field in ptf_fields:
            if args[ptf_field_key] == None:
                #user didnt submit anything to this field group, set false
                setattr(_server,ptf_field,False)
            elif ptf_field in args[ptf_field_key]:
                #user submitted the field, set to true
                setattr(_server,ptf_field,True)
            else:
                #user didnt submit field, set to false
                setattr(_server,ptf_field,False)

    setattr(_server,'ptf_server_name',args['ptf_server_name'])
    setattr(_server,'ptf_steamcommunity_url',args['ptf_steamcommunity_url'])
    setattr(_server,'ptf_site_url',args['ptf_site_url'])
    setattr(_server,'ptf_discord_url',args['ptf_discord_url'])



    setattr(_server,'ptf_datetime_modified',datetime.now())
    setattr(_server,'ptf_modified_ip',str(request.headers.get('X-Forwarded-For')))
    setattr(_server,'ptf_modified_steamid64',str(session['st_id64']))
    db.session.commit()

    ptf_role_dict = {'owner':args['ptf_role_owner'],
                     'admin':args['ptf_role_admin'],
                     'moderator':args['ptf_role_moderator']}

    update_users(ptf_server_id, ptf_role_dict)
    '''
    ptf_server_name
    ptf_server_status

    ptf_site_url
    ptf_steamcommunity_url
    ptf_discord_url
    ptf_discord_private

    


    
    ptf_subregion
    ptf_language

    
    ptf_mirrors_leaguebans
    ptf_match_weekly_frequency
    ptf_match_weekly_frequency_value
    ptf_schedule_day
    ptf_schedule_time
    ptf_schedule_timezone
    ptf_server_owner_name
    ptf_server_owner_discordid
    ptf_server_owner_steamid64
    ptf_date_created
    ptf_datetime_uploaded
    ptf_upload_ip
    ptf_upload_steamid64
'''
    return ''
    if _submitter == None:
        #user hasn't submitted anything yet, add to database as user
        _submitter = htUsers()
        setattr(_submitter,'st_id3',session['st_id3'])
        setattr(_submitter,'st_username',session['display_name'])
        setattr(_submitter,'ht_role',_submitter_role)
        
    else:
        print(_submitter.ht_role)
        _submitter_role = _submitter.ht_role



def update_users(ptf_server_id, ptf_role_dict):
    ''''''
    """

    If the user does not exist for the current server,
        check if steam id id is valid
        add user to table
    If the user does exist for the current server
        If role exists for current user and server, remove role

    list of users and role {st_id64:xxx,st_display_name:xxx,ptf_role:xxx,ptf_server_id:xxx}
    need to check through all 
"""

    '''
    ptf_role_dict = {'owner':[],
                     'admin':[],
                     'moderator':[]}

    ptf_user_dict - {"76xxxx1": {'owner':False,'admin':False,'moderator':False},
                     "76xxxx2": {'owner':False,'admin':False,'moderator':False}}
    '''
    #Create ptf_user_dict from ptf_role_dict
    ptf_user_dict = {}
    for ptf_role, st_id64_list in ptf_role_dict.items():
        if not st_id64_list:
            continue
        for st_id64 in st_id64_list:
            try:
                ptf_user_dict[st_id64][ptf_role] = True
            except:
                ptf_user_dict[st_id64] = {'owner':False,'admin':False,'moderator':False}
                ptf_user_dict[st_id64][ptf_role] = True
        

        
    #get users in the server and check against role_dict
    _users = list(db.session.query(ptfUsers).filter(ptfUsers.ptf_server_id == ptf_server_id))

    #Check if requested users exist, if not, create them here
    existing_user_ids = [_u.st_id64 for _u in _users]
    for requested_user_id in ptf_user_dict.keys():
        if requested_user_id not in existing_user_ids:
            #create empty user entry
            _new_user = ptfUsers()
            setattr(_new_user,'st_id64',requested_user_id)

            _st = steam_query(requested_user_id)
            print('_st',_st[0][requested_user_id]['personaname'])
            display_name = _st[0][requested_user_id]['personaname']
            st_avatar_url = _st[0][requested_user_id]['avatar']
            
            setattr(_new_user,'st_display_name',display_name)
            setattr(_new_user,'st_avatar_url',st_avatar_url)
            setattr(_new_user,'ptf_server_id',ptf_server_id)
            db.session.add(_new_user)
            db.session.commit()

    #If the user wasnt submitted but exists in the database, set ownerships to false
    for existing_user in existing_user_ids:
        if existing_user not in ptf_user_dict.keys():
            ptf_user_dict[existing_user] = {'owner':False,'admin':False,'moderator':False}

    #update user list in case one was added
    _users = list(db.session.query(ptfUsers).filter(ptfUsers.ptf_server_id == ptf_server_id))

    #Check requested roles against existing roles
    for _user in _users:
        if(_user.ptf_server_role_owner and not ptf_user_dict[_user.st_id64]['owner']):
            _user.ptf_server_role_owner = 0
        elif(not _user.ptf_server_role_owner and ptf_user_dict[_user.st_id64]['owner']):
            _user.ptf_server_role_owner = 1

        if(_user.ptf_server_role_admin and not ptf_user_dict[_user.st_id64]['admin']):
            _user.ptf_server_role_admin = 0
        elif(not _user.ptf_server_role_admin and ptf_user_dict[_user.st_id64]['admin']):
            _user.ptf_server_role_admin = 1

        if(_user.ptf_server_role_moderator and not ptf_user_dict[_user.st_id64]['moderator']):
            _user.ptf_server_role_moderator = 0
        elif(not _user.ptf_server_role_moderator and ptf_user_dict[_user.st_id64]['moderator']):
            _user.ptf_server_role_moderator = 1

    db.session.commit()




@pickup.route("/steam_query", methods=['GET'])
def steam_query(_st_id64=None):
    '''Wrapper for SteamAPI GetPlayerSummaries
        _st_id64 can handel single steam id 64 or multiple ids separated by commas'''
    if not _st_id64:
        arg_dic = request.args.to_dict(flat=False)
        try:
            _st_id64 = arg_dic['st_id64']
        except:
            return "Invalid Steam ID"
    
    api_key = current_app.config["STEAM_API_KEY"]
    r = requests.get(f'https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v2/?key={api_key}&steamids={_st_id64}&appid=440')
    players = r.json()['response']['players']
    if len(players) == 0:
        return "No results found, check for valid Steam ID 64", 400
    player_dict = {}
    for p in players:
        player_dict[p['steamid']] = p
    return player_dict, 200