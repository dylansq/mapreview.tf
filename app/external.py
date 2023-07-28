from flask import Blueprint, request, jsonify, redirect, current_app, session
import requests
from .models import ytVideos, tfVersions, ytClips, ytChapters,mrtfHackerTracker
from datetime import datetime
import urllib.parse
from urllib.parse import urlencode
from datetime import datetime, timezone
from dateutil import parser as dtparser
import pytz
import urllib.parse
import json
from .views import get_chapters,get_yt_channel_image
from . import db

external = Blueprint("external", __name__)

@external.route('/opengraphio_clip_query',methods = ['GET'])
def opengraphio_clip_query():
    arg_dic = request.args.to_dict(flat=False)
    try:
        yt_clip_id = arg_dic['yt_clip_id'][0]
    except:
        return "Invalid Steam ID"
    yt_clip_url = urllib.parse.quote('https://www.youtube.com/clip/')
    search_url = f"https://opengraph.io/api/1.1/site/https%3A%2F%2Fwww.youtube.com%2Fclip%2F{yt_clip_id}"
    search_params = {
        'app_id': current_app.config["OPENGRAPH_API_KEY"]
    }
    r = requests.get(search_url,search_params)
    embed_url = r.json()['openGraph']['video']['secure_url']
    clip_title = str(r.json()['openGraph']['title']).replace('\u2702\ufe0f ','')
    p_url = urllib.parse.urlparse(embed_url)
    _yt_video_id = p_url[2].split('/')[-1]
    p_qs = urllib.parse.parse_qs(p_url[4]) #
    _desc = r.json()['openGraph']['description'].split('\u00b7')
    _duration = int(_desc[0].replace("seconds",""))
    _clipper = str(_desc[1]).replace('Clipped by','').strip()
    results = {'yt_clip_id':p_qs['clip'][0],'yt_clipt':p_qs['clipt'][0],'yt_clip_title':clip_title, 'yt_video_id':_yt_video_id,'yt_clip_embed_url':embed_url,'yt_clip_duration':_duration,'yt_clip_clipper':_clipper,'full_opengraph':r.json()['openGraph']}
    return jsonify(results)

@external.route('/lemnoslife_clip_query',methods = ['GET'])
def lemnoslife_clip_query():
    arg_dic = request.args.to_dict(flat=False)
    try:
        yt_clip_id = arg_dic['yt_clip_id'][0]
    except:
        return "Invalid Steam ID"
    search_url = 'https://yt.lemnoslife.com/videos'
    search_params = {
        'clipId': yt_clip_id,
        'part': 'id'
    }
    r = requests.get(search_url,search_params)
    print(search_url)
    print(r)
    return r.json()

@external.route('/lemnoslife_chapter_query',methods = ['GET'])
def lemnoslife_chapter_query(yt_video_id=None):
    
    if not yt_video_id:
        arg_dic = request.args.to_dict(flat=False)
        yt_video_id = arg_dic['yt_video_id'][0]

    
    print('llchaptquer')
    print(get_chapters(yt_video_id=yt_video_id)[1])
    print(get_chapters(yt_video_id=yt_video_id)[0])
    if  get_chapters(yt_video_id=yt_video_id)[1] != 204:
        print("chapters already exist")
        return '', 204


    search_url = 'https://yt.lemnoslife.com/videos'
    search_params = {
        'id': yt_video_id,
        'part': 'chapters'
    }
    r = requests.get(search_url,search_params)
    print(search_url)
    if r.status_code == 500:
        return ''
    
    if r.json()['items'][0]['chapters']['areAutoGenerated'] == 'false':
        _autogen = 0 #uploader generated chapter
    else:
        _autogen = 1 #youtube autogenerated chapters
    _chapters = r.json()['items'][0]['chapters']['chapters']
    _final_chapters = {}
    for i, _c in enumerate(_chapters):
        yt_chapter_id = f"{yt_video_id}-{i}"
        _final_chapters[yt_chapter_id] = {
            'yt_chapter_id': yt_chapter_id,
            'yt_video_id': yt_video_id,
            'yt_chapter_title': _c['title'],
            'yt_chapter_start': float(_c['time']),
            'yt_chapter_autogenerated': _autogen,
            'mrtf_upload_datetime': datetime.now()
        }
        submit_yt_chapter(_final_chapters[yt_chapter_id]) 
    return jsonify(_final_chapters)


def submit_yt_chapter(_ytc):
    _chapter = ytChapters()
    for k,v in _ytc.items():
        setattr(_chapter,k,v)

    db.session.add(_chapter)
    db.session.commit()
    return None

@external.route('/steam_rep_query',methods = ['GET'])
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

@external.route('/steam_query',methods = ['GET'])
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


@external.route('/ht_get_recently_played', methods=['GET'])
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


@external.route('/ht_get_last_played_tf2', methods=['GET'])
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

@external.route('/ht_update_all_steam', methods=['GET'])
def ht_update_all_steam():
    _hackers  = mrtfHackerTracker.query.all()
    for _hacker in _hackers:
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
    return ''







@external.route('/ht_update_all_steamrep', methods=['GET'])
def ht_update_all_steamrep():
    _hackers  = mrtfHackerTracker.query.all()
    for _hacker in _hackers:
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

    return ''



@external.route("/steam_auth")
def auth_with_steam(origin=None):
    arg_dic = request.args.to_dict(flat=False)
    host = '://'.join(urllib.parse.urlparse(request.base_url)[:2])
    try:
        origin = 'origin='+ str(arg_dic['origin'][0])
    except:
        origin = "origin=https://mapreview.tf"

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

def SteamID64To3(st_id64):
    steamID64IDEnt = 76561197960265728
    id3base = int(st_id64) - steamID64IDEnt
    return ("[U:1:{0}]".format(id3base),id3base)

@external.route("/authorize")
def authorize():
    arg_dic = request.args.to_dict(flat=False)
    try:
        origin = arg_dic['origin'][0]
    except:
        origin = "https://mapreview.tf"
    
    try:
        identity = request.args['openid.identity']
        
        session['st_id64'] = identity.split('/')[-1]
        session['st_id3'] = SteamID64To3(identity.split('/')[-1])[1]
    except:
        print("error with steam auth")
    #session['st_id64'] = 
    sq = steam_query(session['st_id64'])['response']['players']
    print('sq: ',sq)
    try:
        sq = steam_query(session['st_id64'])['response']['players'][0]
        print(sq)
        session['display_name'] = sq['personaname']
        session['avatar_url'] = sq['avatarfull']
    except:
        pass
    print(session)
    return redirect(origin)

@external.route("/steam_logout")
def steam_logout():
    session.clear()
    host = '://'.join(urllib.parse.urlparse(request.base_url)[:2])
    return redirect(host)

#old?

@external.route("/st") 
def hello():
    return '<a href="http://localhost:5000/auth">Login with steam</a>'



@external.route('/twitch_auth',methods=['GET','POST'])
def twitch_auth():
    #Client credentials grant flow
    search_url= 'https://id.twitch.tv/oauth2/token'
    search_params = {
        'client_id':current_app.config["TWITCH_CLIENT_ID"],
        'client_secret':current_app.config["TWITCH_CLIENT_SECRET"],
        'grant_type':"client_credentials"
    }
    r = requests.post(search_url,search_params)
    return r.json()

@external.route('/twitch')
def twitch():
    arg_dic = request.args.to_dict(flat=False)
    try:
        twitch_video_id = arg_dic['twitch_video_id']
    except:
        twitch_video_id = "1736735696"
    
    _token = twitch_auth()
    headers = {
        'Authorization': "Bearer " + _token['access_token'],
        'Client-Id': current_app.config["TWITCH_CLIENT_ID"]
        }
    print(headers)
    search_url = "https://api.twitch.tv/helix/videos"
    search_params = {
        'id':twitch_video_id}
    r = requests.get(search_url,search_params,headers=headers)
    print(r)
    return r.json()
    return render_template('twitch.html')



@external.route('/refresh_yt_stats', methods=['POST'])
def refresh_yt_stats():
    '''Fetch stats for all videos from Youtube V3 API and update database entries'''
    _videos = ytVideos.query.all()
    for _vid in _videos:
        search_url = "https://www.googleapis.com/youtube/v3/videos"
        search_params = {
            'key': current_app.config["YOUTUBE_API_KEY"],
            'part':"snippet,statistics",
            "id":_vid.yt_video_id}
        r = requests.get(search_url,search_params)
        _stats = r.json()["items"][0]["statistics"]
        _snip = r.json()["items"][0]["snippet"]
        _data = {}
        _keyvalues = [
            ("yt_stats_views",_stats["viewCount"]),
            ("yt_stats_likes",_stats["likeCount"]),
            ("yt_stats_favorites",_stats["favoriteCount"]),
            ("yt_stats_comments",_stats["commentCount"]),
            ("yt_channel_title",_snip["channelTitle"]),
            ("yt_channel_id",_snip["channelId"]),
            ("yt_video_description",_snip["localized"]["description"]),
            ("yt_video_title",_snip["localized"]["title"]),
            ("yt_published_date",dtparser.parse(_snip["publishedAt"])),
            ("yt_stats_lastupdated",datetime.now(pytz.utc)),
            ("yt_channel_image",get_yt_channel_image(_snip["channelId"]))
        ]
        #Some videos didn't have some keys, if key doesnt exist, skip
        for k,v in _keyvalues:
            try:
                _data[k] = v
            except:
                print(f'Could not retrieve youtube data {k} for {_vid.yt_video_id}')

        _data = {}#"yt_video_thumbnails":_snip["thumbnails"]
        #print(_data)
        
        for key, value in _data.items():
            setattr(_vid, key, value)
            print("setting ",key," to ",value, " for ",_vid.yt_video_id)
        
        try:
            lemnoslife_chapter_query(_vid.yt_video_id)
        except:
            pass


        #update algorithm
        #print('chapters')
        print(_vid.yt_video_id)
        _gc = get_chapters(yt_video_id=_vid.yt_video_id)
        #print("_a :", _gc[0].json)
        chapter_count = len(_gc[0].json)
        
        chapter_score = min(5.,float(chapter_count))/5 #linear scale up to 5 chapters
        try:
            days_old = (datetime.now(timezone.utc) - _vid.yt_published_date).days
        except:
            days_old = (datetime.now() - _vid.yt_published_date).days
            
        age_score = (1-min(1.0,days_old/2191))**4
        likes_score = min(1,(float(_vid.yt_stats_likes)/100)**0.5)
        views_score = min(1,(float(_vid.yt_stats_views)/2000))
        ratio_score = max(1.0,10*float(_vid.yt_stats_likes)/float(_vid.yt_stats_views))

        mrtf_rating_score_a1 = int(100*(age_score*2 + likes_score + views_score + ratio_score + chapter_score)/6)
        setattr(_vid,"mrtf_rating_score_a1",mrtf_rating_score_a1)

        db.session.commit()

    return '', 200


