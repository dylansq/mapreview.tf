from flask import Blueprint, render_template, request, flash, url_for, jsonify,redirect, current_app, send_from_directory, Response
import requests, time
from .models import mrtfHackerTracker
from datetime import datetime
import urllib.parse
from urllib.parse import urlencode
from datetime import datetime, timezone
from dateutil import parser as dtparser
import pytz
import re
import urllib.parse
import json
from . import db
from werkzeug.utils import secure_filename
from sqlalchemy import or_, and_
from webargs import  validate
from webargs.flaskparser import parser, abort, use_args
from marshmallow import Schema, fields, EXCLUDE, missing



ht = Blueprint("hackertracker", __name__)

#'cheater' - Player manually controlling a(n) account(s) that are using a script/program to cheat
#'bot' - Automatically controlled account using a script/program to cheat
#'racist' - Racist
#'annoying' - Non-cheater who was temporarily muted for any reason

class htFormSchema(Schema):
    st_id64 = fields.Str(required=True,validate=[validate.Length(16,17)])
    ht_reason = fields.Str(validate=[validate.OneOf(['cheater','bot','racist','annoying'])])
    ht_confidence = fields.Float()
    ht_gamemode = fields.Str(validate=[validate.OneOf(['valvecomp','casual','communitycomp','mvm','other'])])

    class Meta:
        unknown = EXCLUDE

@ht.route('/', methods=['GET'])
def hacker_tracker():
    _hackers = mrtfHackerTracker.query.all()
    #array for display
    sr_vac = ["","Banned"]
    st_privacy = ['Private','Unused','Public']
    st_state = ['Offline','Online','Busy','Away','Snooze','Other','Other']
    return render_template('./hacker_tracker.html',hackers =_hackers,sr_vac = sr_vac,st_privacy=st_privacy,st_state=st_state)


@ht.route('/check_existing_hackers', methods=['GET'])
def check_existing_hackers(st_id64=None):
    if st_id64 is None:
        arg_dic = request.args.to_dict(flat=False)
        st_id64 = arg_dic['st_id64'][0]
    else:
        pass
    
    #return 'invalid st_id64'

    if len(st_id64) != 17:
        return f'Invalid Steam ID: "{st_id64:17.17}..."\nUse SteamID64 format\neg. "76561198082222131"' ,400

    _hackers  = db.session.query(mrtfHackerTracker).filter(mrtfHackerTracker.st_id64.in_([st_id64]))
    _count = len(list(_hackers))
    if _count != 0:
        return f'Steam ID already in database: {st_id64}', 400
    
    if len(steam_query(st_id64)["response"]["players"]) != 1:
        return f'Invalid Steam ID: {st_id64}\nUse SteamID64 format\neg. "76561198082222131"' ,400

    
    return jsonify({'count':len(list(_hackers))}), 200

@ht.route('/submit_hacker', methods=['POST'])
@use_args(htFormSchema(), location='form', unknown=None)
def submit_hacker(args):
    '''Accept POST request for hacker submit'''
    print(f"args: {args}")

    _hacker = mrtfHackerTracker()
    setattr(_hacker,'ht_datetime_added',datetime.now())
    for k,v in args.items():
        #use dateutil.parse to parse dates - more robust than webargs/marshmallow
        if 'date' in k:
            v = dtparser.parse(v)
        setattr(_hacker,k,v)

    try:
        print(str(request.headers.get('X-Forwarded-For'))) #PythonAnywhere forwards ip requests in headder from local IP
        setattr(_hacker,"ht_uploadip",str(request.headers.get('X-Forwarded-For')))
    except:
        print('ipgetttingfailed')

    #validate objects
    try:
        print("check_existing_hackers: ",check_existing_hackers(_hacker.st_id64))
        print("st_id64: ",_hacker.st_id64)
        _count = check_existing_hackers(_hacker.st_id64)[0].json['count']
    except KeyError:
        return f'Invalid Steam ID\nUse SteamID64 format\neg. "76561198082222131"' ,400
    
    print("check existing: ",_count)
    if _count != 0:
        return jsonify({'error':f'Steam ID already in database: {_hacker.st_id64}'}), 400
    
    if len(steam_query(_hacker.st_id64)["response"]["players"]) != 1:
        print('len: ',len(steam_query(_hacker.st_id64)["response"]["players"]))
        return f'Invalid Steam ID: {_hacker.st_id64}\nUse SteamID64 format\neg. "76561198082222131"' ,400

    db.session.add(_hacker)
    db.session.commit()

    ht_update_steam(_hacker)
    #https://api.steampowered.com/ISteamUser/GetPlayerBans/v1?key={key}&steamids=76561199443667030&appid=440
    return '',200


@ht.route('/cheaters', methods=['GET'])
def show_cheaters():
    return send_from_directory('static/txt/','cheaters.txt')


tf2_botlist_urls = {
        #"Pazer": "https://raw.githubusercontent.com/PazerOP/tf2_bot_detector/master/staging/cfg/playerlist.official.json", #Pazer's list of bots
        #"Chev": "https://raw.githubusercontent.com/chev2/tf2-voice-ban-bots/master/voice_ban_users.json", #My list of bots
        #"wgetJane": "https://gist.githubusercontent.com/wgetJane/0bc01bd46d7695362253c5a2fa49f2e9/raw/fefb98e0e10bbab8ff1b38e96adbaabf4a8db94f/bot_list.txt", #wgetJane's list of bots
        "mapreviewtf":"https://mapreview.tf/ht/cheaters"}

def SteamID64To3(st_id64):
    steamID64IDEnt = 76561197960265728
    id3base = int(st_id64) - steamID64IDEnt
    return ("[U:1:{0}]".format(id3base),id3base)

@ht.route('/upload_voice_ban_dt', methods=['POST'])
def upload_voice_ban_dt(unmute_annoying=None):
    if not unmute_annoying:
        arg_dic = request.args.to_dict(flat=False)
        try:
            unmute_annoying = eval(arg_dic['unmute_annoying'][0])
        except:
            unmute_annoying = False

    steamid3_regex = r'(\[U:1:\d+\])'
    f = request.files['file']
    if secure_filename(f.filename) != "voice_ban.dt":
        print("Bad Filename")
        return ''
    st_id3s = []
    #print(f)
    for r in f:
        #print(r)
        st_id3s.extend(re.findall(steamid3_regex,str(r)))   #.decode('UTF-8')
    #print(f"request.file: {f}")
    #print(st_id3s)
    return combine_mutes(st_id3s,unmute_annoying), 200

@ht.route('/mutes', methods=['GET'])
def combine_mutes(existing_mutes,unmute_annoying=False):
    print("unmuting is ",unmute_annoying)
    steamIDlen = 32

    steamid3_regex = r'(\[U:1:\d+\])'
    wgetjane_list_regex = r'\n(\d+)'

    players = []

    
    ## new from db
    players = list(db.session.execute(db.session.query(mrtfHackerTracker).filter(and_(mrtfHackerTracker.ht_reason.in_(["cheater","bot"]),mrtfHackerTracker.ht_confidence>= 0.9))))
    
    players = [SteamID64To3(str(x[0].st_id64))[0] for x in players]
    
    #print(players)
    print(f"{len(players)} accounts found in database")
    print(f"{len(existing_mutes)} accounts sent from user")
    #new from db end

    players.extend(existing_mutes) #add the user-provided mutes to the grabbed player mutes
    if unmute_annoying:
        unmute = list(db.session.execute(db.session.query(mrtfHackerTracker).filter(mrtfHackerTracker.ht_reason.in_(["annoying"]))))
        unmute = [SteamID64To3(str(x[0].st_id64))[0] for x in unmute]

        l1 = len(players)
        players = [x for x in players if x not in unmute]
        l2 = len(players)
        print(f"removed {l1-l2} account(s) previously muted")

    dupe_number = len(players) - len(set(players)) #get number of duplicates
    players = sorted(set(players), key=lambda x: len(x)) #remove duplicates in case of merging, also sort by ID length (the voice_ban.dt file will break if not sorted)

    for player in range(0, len(players)):
        
        players[player] += "\0"*(steamIDlen-len(players[player])) #steam ID length plus whitespace should always equal 32 characters

    players_as_string = "\x01\0\0\0" + ''.join(players) #this is how the voice_ban.dt file is patterned

    print(f"{format(len(players), ',d')} muted players in total. Removed {dupe_number} duplicates.")

    #print(players_as_string)
    return players_as_string


@ht.route('/hacker_ids', methods=['GET'])
def hacker_ids():
    players = list(db.session.execute(db.session.query(mrtfHackerTracker).filter(and_(mrtfHackerTracker.ht_reason.in_(["cheater","bot"]),mrtfHackerTracker.ht_confidence>= 0.99))))
    
    return Response('\n'.join([p[0].st_id64 for p in players]),mimetype='text/plain')


@ht.route('/ht_get_all_rich_presence', methods=['GET'])
def ht_get_all_rich_presence(st_id64=None):
    _hackers  = mrtfHackerTracker.query.all()
    i = 0
    j = 0
    times = [15, 5, 5, 1, 1, 0.1]
    for _hacker in _hackers:
        if j%5==0:
            time.sleep(3)
        j +=1
        status = ht_get_rich_presence(_hacker.st_id64)[1]
        if status == 200:
            continue
        elif status == 500:
            time.sleep(times[i])
            i +=1
            if i > len(times)-1:
                i = len(times)-1
    return ''



@ht.route('/playerlist.valvecomp_cheaters.json', methods=['GET'])
def valvecomp_cheaters():
    cheater_results = list(db.session.execute(db.session.query(mrtfHackerTracker).filter(and_(mrtfHackerTracker.ht_reason.in_(["cheater","bot","racist"]),mrtfHackerTracker.ht_confidence>= 0.99))))
    
    players = [{'attributes':[p[0].ht_reason],'steamid':SteamID64To3(p[0].st_id64)[0]} for p in cheater_results]

    valvecomp_dict = {
        "$schema": "https://raw.githubusercontent.com/PazerOP/tf2_bot_detector/master/schemas/v3/playerlist.schema.json",
        'file_info':{
            'authors':['Zebulon','Fuzzycoco','Plasic74x','Arthur'],
            'description':'List of cheaters, hackers, aimbots, and racists who queue for North American Valve Competitive Matchmaking',
            'title':"YAVC's Valve Comp Hacker Tracker",
            'update_url':'https://mapreview.tf/ht/playerlist.valvecomp_cheaters.json'
        },
        'players':players}
    
    return jsonify(valvecomp_dict)


@ht.route('/ht_get_rich_presence', methods=['GET'])
def ht_get_rich_presence(st_id64=None):
    if not st_id64:
        arg_dic = request.args.to_dict(flat=False)
        try:
            st_id64 = arg_dic['st_id64'][0]
        except:
            return "Invalid Steam ID"
    st_id3 = SteamID64To3(st_id64)[1]
    print(f'https://steamcommunity.com/miniprofile/{st_id3}/json')
    r = requests.get(f'https://steamcommunity.com/miniprofile/{st_id3}/json')
    

    _data = {}
    try:

        _data["st_rich_presence_game"] = str(r.json()['in_game']['name'])
        _data["st_rich_presence_desc"] = str(r.json()['in_game']['rich_presence'])
        _data["st_rich_presence_datetime_updated"] = datetime.now(pytz.utc)
        #print(r.json()['in_game']['name'])
        #print(r.json()['in_game']['rich_presence'])
    except KeyError:
        print("key eerror for: ", st_id64)
        _data["st_rich_presence_game"] = None
        _data["st_rich_presence_desc"] = None
        _data["st_rich_presence_datetime_updated"] = None
        
        pass
    except Exception as err:
        try:
            print(f"other error {err} for: {st_id64}")
            print(r.content)
            r = requests.get(f'https://steamcommunity.com/miniprofile/{st_id3}/json')
            _data["st_rich_presence_game"] = str(r.json()['in_game']['name'])
            _data["st_rich_presence_desc"] = str(r.json()['in_game']['rich_presence'])
            _data["st_rich_presence_datetime_updated"] = datetime.now(pytz.utc)
            
            
            
        except Exception as err2:
            return '',500
    _hacker  = list(db.session.execute(db.session.query(mrtfHackerTracker).filter(mrtfHackerTracker.st_id64.in_([st_id64]))))[0][0]
    


    for key, value in _data.items():
        #print("setting {} to {} for {}".format(key,value,_hacker.st_id64))
        setattr(_hacker, key, value)
    
    #print(_hacker)
    db.session.commit()

    return '',200

@ht.route('/ht_get_recently_played', methods=['GET'])
def ht_get_recently_played(_st_id64=None):
    '''Returns hours of tf2 hours played in the last two weeks. If not available, returns -1'''
    if not _st_id64:
        arg_dic = request.args.to_dict(flat=False)
        try:
            _st_id64 = arg_dic['st_id64'][0]
        except:
            return "Invalid Steam ID"
    
    api_key = current_app.config["STEAM_API_KEY"]
    r = requests.get(f'https://api.steampowered.com/IPlayerService/GetRecentlyPlayedGames/v1/?key={api_key}&steamid={_st_id64}')
    
    try:
        tf2_entry = None
        games = r.json()['response']['games']
        for entry in games:
            if entry['appid'] == 440:
                tf2_entry = entry
        
        if tf2_entry == None:
            #no tf2 entry found in list
            return jsonify({"st_hours_played_2weeks":0})
        
        tf2_hrs_2weeks = float(tf2_entry['playtime_2weeks'])/60
        #print(r.json()['response']['games'][0])
        return jsonify({"st_hours_played_2weeks":tf2_hrs_2weeks})
    except:
        return jsonify({"st_hours_played_2weeks":-1.})


@ht.route('/ht_get_last_played_tf2', methods=['GET'])
def ht_get_last_played_tf2(_st_id64=None):
    '''Returns hours of tf2 hours played in the last two weeks. If not available, returns -1'''
    if not _st_id64:
        arg_dic = request.args.to_dict(flat=False)
        try:
            _st_id64 = arg_dic['st_id64'][0]
        except:
            return "Invalid Steam ID"
    
    api_key = current_app.config["STEAM_API_KEY"]
    r = requests.get(f'https://api.steampowered.com/IPlayerService/GetOwnedGames/v1/?key={api_key}&steamid={_st_id64}&include_played_free_games=1')
    
    try:
        tf2_entry = None
        games = r.json()['response']['games']
        for entry in games:
            if entry['appid'] == 440:
                tf2_entry = entry
                if tf2_entry['rtime_last_played'] == 0:
                    return jsonify({"st_last_played":None})
                return jsonify({"st_last_played":tf2_entry['rtime_last_played']})

        if tf2_entry == None:
            #no tf2 entry found in list
            return jsonify({"st_last_played":None})
    except:
        return jsonify({"st_last_played":None})

@ht.route('/steam_query',methods = ['GET'])
def steam_query(_st_id64=None):
    if not _st_id64:
        arg_dic = request.args.to_dict(flat=False)
        try:
            _st_id64 = arg_dic['st_id64']
        except:
            return "Invalid Steam ID"
    
    api_key = current_app.config["STEAM_API_KEY"]
    r = requests.get(f'https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v2/?key={api_key}&steamids={_st_id64}&appid=440')
    return r.json()



@ht.route('/ht_update_all_steam', methods=['GET'])
def ht_update_all_steam():
    _hackers  = mrtfHackerTracker.query.all()
    for _hacker in _hackers:
        ht_update_steam(_hacker)
    return ''

def ht_update_steam(_hacker):
    _st_id64 = _hacker.st_id64
    _st = steam_query(_st_id64=_hacker.st_id64)
    _st = _st["response"]["players"][0] #only handel one user. api method can handel multiple though
    
    hoursplayed = ht_get_recently_played(_st_id64).json['st_hours_played_2weeks']
    _lastplayed = ht_get_last_played_tf2(_st_id64).json['st_last_played']
    #print('lastplayed: ',lastplayed)
    try:
        _timecreated = datetime.utcfromtimestamp(int(_st["timecreated"]))
    except:
        _timecreated = None

    try:
        _lastlogoff = datetime.utcfromtimestamp(int(_lastplayed))
    except:
        _lastlogoff = None
    
    _kvp = [("st_communityvisibilitystate","communityvisibilitystate"),
                ("st_profilestate","profilestate"),
                ("st_personaname","personaname"),
                ("st_commentpermission","commentpermission"),
                ("st_profile_url","profileurl"),
                ("st_avatar_url","avatar"),
                ("st_avatarmedium_url","avatarmedium"),
                ("st_avatarfull_url","avatarfull"),
                ("st_avatarhash","avatarhash"),
                ("st_personastate","personastate"),
                ("st_primaryclanid","primaryclanid"),
                ("st_personastateflags","personastateflags"),
                ("st_realname","realname")]

    _data = {}
    _data["st_lastlogoff"] = _lastlogoff
    _data["st_hours_played_2weeks"] = hoursplayed
    _data["st_lastupdate_datetime"] = datetime.now(pytz.utc)
    #_data["st_lastlogoff"] = _lastlogoff
    #use st_lastlogoff as st_last_played...
    _data["st_timecreated"] = _timecreated

    for k,v in _kvp:
        try:
            _data[k] = _st[v]
        except:
            print(f"Error setting value for {k} for {v}")
            pass

    for key, value in _data.items():
        setattr(_hacker, key, value)

    db.session.commit()

@ht.route('/steam_rep_query',methods = ['GET'])
def steam_rep_query(st_id64=None):
    if not st_id64:
        arg_dic = request.args.to_dict(flat=False)
        try:
            st_id64 = arg_dic['st_id64']
        except:
            return "Invalid Steam ID"
    
    r = requests.get(f'https://steamrep.com/api/beta4/reputation/{st_id64}?extended=1&json=1')
    print(r.text)
    return r.json()

def ht_update_steamrep(_hacker):
    _sr = steam_rep_query(_hacker.st_id64)
    _sr = _sr["steamrep"]
    try:
        _membersince = datetime.utcfromtimestamp(int(_sr["membersince"]))
    except:
        _membersince = None
    try:
        _lastsynctime = datetime.utcfromtimestamp(int(_sr["lastsynctime"]))
    except:
        _lastsynctime = None
    _data = {"sr_steamrepurl":_sr["steamrepurl"],
                "sr_displayname":_sr["displayname"],
                "sr_rawdisplayname":_sr["rawdisplayname"],
                "sr_customurl":_sr["customurl"],
                "sr_avatar":str(_sr["avatar"]),
                "sr_membersince":_membersince,
                "sr_lastsynctime":_lastsynctime,
                "sr_tradeban":_sr["tradeban"],
                "sr_vacban":_sr["vacban"],
                "sr_lastupdate_datetime":datetime.now(pytz.utc)}

    for key, value in _data.items():
        setattr(_hacker, key, value)

    db.session.commit()


@ht.route('/ht_update_all_steamrep', methods=['GET'])
def ht_update_all_steamrep():
    _hackers  = mrtfHackerTracker.query.all()
    for _hacker in _hackers:
        ht_update_steamrep(_hacker)

    return ''