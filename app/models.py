from . import db
from sqlalchemy.sql import func
from dataclasses import dataclass
from datetime import datetime

'''
Prefixes
yt: youtube 
st: steam
sr: steamrep.com
tf: teamfortress2
mrtf: mapreview.tf
tw: twitch
'''



class ytVideos(db.Model):
    yt_video_id= db.Column(db.String(32), unique= True,primary_key=True)
    yt_account= db.Column(db.String(64))
    st_creator_name= db.Column(db.String(32))
    st_creator_id= db.Column(db.String(32))
    st_haspresenter= db.Column(db.Integer)
    st_presenter_name= db.Column(db.String(32))
    st_presenter_id= db.Column(db.String(32))
    yt_date_uploaded= db.Column(db.DateTime(timezone=True))
    yt_date_recorded= db.Column(db.DateTime(timezone=True))
    mrtf_upload_datetime= db.Column(db.DateTime(timezone=True))
    mrtf_upload_ip= db.Column(db.String(64))
    mrtf_upload_steam_id= db.Column(db.String(64))
    mrtf_display_name= db.Column(db.String(200))
    mrtf_display_id= db.Column(db.String(200))
    mrtf_language= db.Column(db.String(64))
    tf_map_full= db.Column(db.String(32))
    tf_version_full= db.Column(db.String(64))
    relevant_classes= db.Column(db.String(64))
    #
    tf_match_format= db.Column(db.String(32)) 
    tf_class_all= db.Column(db.Integer)
    tf_class_none= db.Column(db.Integer)
    tf_class_scout= db.Column(db.Integer)
    tf_class_soldier= db.Column(db.Integer)
    tf_class_demo= db.Column(db.Integer)
    tf_class_medic= db.Column(db.Integer)
    tf_class_engineer= db.Column(db.Integer)
    tf_class_pyro= db.Column(db.Integer)
    tf_class_heavy= db.Column(db.Integer)
    tf_class_sniper= db.Column(db.Integer)
    tf_class_spy= db.Column(db.Integer)
    tf_role= db.Column(db.String(64))
    tf_role_combo= db.Column(db.Integer)
    tf_role_flank= db.Column(db.Integer)
    tf_role_offclass= db.Column(db.Integer)
    tf_league= db.Column(db.String(16))
    tf_skill_level= db.Column(db.String(16))
    tf_resource_type= db.Column(db.String(32))
    tf_has_teamcoms= db.Column(db.Integer)
    yt_channel_title= db.Column(db.String(100))
    yt_channel_id= db.Column(db.String(32))
    yt_video_title= db.Column(db.String(100))
    yt_published_date= db.Column(db.DateTime(timezone=True))
    yt_channel_image= db.Column(db.String(200))
    yt_stats_lastupdated= db.Column(db.DateTime(timezone=True))
    yt_stats_comments= db.Column(db.Integer)
    yt_stats_favorites= db.Column(db.Integer)
    yt_stats_likes= db.Column(db.Integer)
    yt_stats_views= db.Column(db.Integer)
    yt_stats_likes_views_ratio= db.Column(db.Float)
    
    mrtf_rating_score_a1= db.Column(db.Integer)


    def __init__(self, **kwargs):
        super(ytVideos, self).__init__(**kwargs)

class ytClips(db.Model):
    yt_clip_id= db.Column(db.String(32),unique= True, primary_key=True)
    yt_video_id= db.Column(db.String(32))
    yt_account= db.Column(db.String(64))
    #
    #
    #
    #
    #
    #
    #
    #
    #
    st_creator_name= db.Column(db.String(32))
    st_creator_id= db.Column(db.String(32))
    mrtf_upload_datetime= db.Column(db.DateTime(timezone=True))
    mrtf_upload_ip= db.Column(db.String(64))
    mrtf_upload_steam_id= db.Column(db.String(64))
    mrtf_language= db.Column(db.String(64))
    tf_map_full= db.Column(db.String(32))
    tf_version_full= db.Column(db.String(64))
    tf_match_format= db.Column(db.String(32)) 
    tf_class_all= db.Column(db.Integer)
    tf_class_none= db.Column(db.Integer)
    tf_class_scout= db.Column(db.Integer)
    tf_class_soldier= db.Column(db.Integer)
    tf_class_demo= db.Column(db.Integer)
    tf_class_medic= db.Column(db.Integer)
    tf_class_engineer= db.Column(db.Integer)
    tf_class_pyro= db.Column(db.Integer)
    tf_class_heavy= db.Column(db.Integer)
    tf_class_sniper= db.Column(db.Integer)
    tf_class_spy= db.Column(db.Integer)
    tf_role= db.Column(db.String(16))
    tf_role_combo= db.Column(db.Integer)
    tf_role_flank= db.Column(db.Integer)
    tf_role_offclass= db.Column(db.Integer)

    tf_league= db.Column(db.String(16))
    tf_skill_level= db.Column(db.String(16))
    tf_resource_type= db.Column(db.String(32))
    tf_has_teamcoms= db.Column(db.Integer)

    yt_channel_title= db.Column(db.String(100))
    yt_channel_id= db.Column(db.String(32))
    yt_video_title= db.Column(db.String(200))
    yt_published_date= db.Column(db.DateTime(timezone=True))
    yt_channel_image= db.Column(db.String(200))
    #
    #
    #
    #
    #
    yt_clip_title= db.Column(db.String(200))
    yt_clip_duration= db.Column(db.Integer)
    yt_clip_clipper= db.Column(db.String(64))
    yt_clipt= db.Column(db.String(32))


    def __init__(self, **kwargs):
        super(ytClips, self).__init__(**kwargs)

@dataclass
class ytChapters(db.Model):
    yt_chapter_id:str = db.Column(db.String(32),unique= True, primary_key=True)
    yt_video_id:str = db.Column(db.String(32))
    #
    yt_chapter_start:float = db.Column(db.Float)
    yt_chapter_end:float = db.Column(db.Float)
    yt_chapter_duration:float = db.Column(db.Float)
    yt_chapter_title:str = db.Column(db.String(200))

    yt_chapter_autogenerated:int = db.Column(db.Integer)
    mrtf_upload_datetime:datetime = db.Column(db.DateTime(timezone=True))
    mrtf_upload_ip:str = db.Column(db.String(64))
    mrtf_upload_steam_id:str = db.Column(db.String(64))
    resource_type:str = db.Column(db.String(32))
    #
    tf_map_full:str = db.Column(db.String(32))
    tf_version_full:str = db.Column(db.String(64))
    #
    #
    #
    tf_class_all:int = db.Column(db.Integer)
    tf_class_none:int = db.Column(db.Integer)
    tf_class_scout:int = db.Column(db.Integer)
    tf_class_soldier:int = db.Column(db.Integer)
    tf_class_demo:int = db.Column(db.Integer)
    tf_class_medic:int = db.Column(db.Integer)
    tf_class_engineer:int = db.Column(db.Integer)
    tf_class_pyro:int = db.Column(db.Integer)
    tf_class_heavy:int = db.Column(db.Integer)
    tf_class_sniper:int = db.Column(db.Integer)
    tf_class_spy:int = db.Column(db.Integer)
    tf_role:str = db.Column(db.String(16))
    #
    #
    #
    #
    #
    resource_type:str = db.Column(db.String(32))
    #
    #
    #
    yt_chapter_submitted_by_name:str = db.Column(db.String(64))
    yt_chapter_submitted_by_id:str = db.Column(db.String(64))



    def __init__(self, **kwargs):
        super(ytChapters, self).__init__(**kwargs)


class Versions(db.Model):
    tf_version_full =db.Column(db.String(32), unique = True, primary_key = True)
    version_order = db.Column(db.String(32))
    version_iscurrent = db.Column(db.Integer())
    tf_map_full = db.Column(db.String(32))
    map_name = db.Column(db.String(32))
    

class tfVersions(db.Model):
    tf_version_full= db.Column(db.String(32),unique= True, primary_key=True)
    tf_map_full= db.Column(db.String(64))
    tf_map_name= db.Column(db.String(64))
    tf_map_format= db.Column(db.String(64))
    tf_match_format= db.Column(db.String(32)) 
    tf_version_release_date= db.Column(db.DateTime(timezone=True))
    tf_version_iscurrent = db.Column(db.Boolean())
    tf_version_display= db.Column(db.Boolean())
    tf_resource_url= db.Column(db.String(64))
    tf_version_provisional=db.Column(db.Boolean())


    def __init__(self, **kwargs):
        super(tfVersions, self).__init__(**kwargs)


class mrtfHackerTracker(db.Model):
    st_id64= db.Column(db.String(32), unique= True,primary_key=True)
    st_id3= db.Column(db.String(64))
    ht_reason= db.Column(db.String(32))
    ht_confidence= db.Column(db.Float)
    ht_datetime_added= db.Column(db.DateTime(timezone=True))
    ht_gamemode= db.Column(db.String(32))
    ht_uploadip= db.Column(db.String(32))

    sr_steamrepurl= db.Column(db.String(128))
    sr_displayname= db.Column(db.String(64))
    sr_rawdisplayname= db.Column(db.String(64))
    sr_customurl= db.Column(db.String(64))
    sr_avatar= db.Column(db.String(128))
    sr_lastupdate_datetime= db.Column(db.DateTime(timezone=True))
    sr_membersince= db.Column(db.DateTime(timezone=True))
    sr_lastsynctime= db.Column(db.DateTime(timezone=True))
    sr_tradeban= db.Column(db.Integer)
    sr_vacban= db.Column(db.Integer)
    
    st_lastupdate_datetime= db.Column(db.DateTime(timezone=True))
    st_communityvisibilitystate= db.Column(db.Integer)
    st_profilestate= db.Column(db.Integer)
    st_personaname= db.Column(db.String(64))
    st_commentpermission= db.Column(db.Integer)
    st_profile_url= db.Column(db.String(128))
    st_avatar_url= db.Column(db.String(300))
    st_avatarmedium_url= db.Column(db.String(300))
    st_avatarfull_url= db.Column(db.String(300))
    st_avatarhash= db.Column(db.String(64))
    st_personastate= db.Column(db.Integer)
    st_primaryclanid= db.Column(db.String(64))
    st_timecreated= db.Column(db.DateTime(timezone=True))
    st_personastateflags= db.Column(db.Integer)
    st_lastlogoff= db.Column(db.DateTime(timezone=True))
    st_realname= db.Column(db.String(64))
    st_hours_played_2weeks= db.Column(db.Float)
    st_rich_presence_game = db.Column(db.String(64))
    st_rich_presence_desc= db.Column(db.String(64))
    st_rich_presence_datetime_updated= db.Column(db.DateTime(timezone=True))


    def __init__(self, **kwargs):
        super(mrtfHackerTracker, self).__init__(**kwargs)

