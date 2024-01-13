import discord
from discord.ext import commands

import datetime
import asyncio
import aiohttp
import urllib
import time

import yaml
import sqlalchemy as sa
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.exc import SQLAlchemyError

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import AsyncSession



intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.voice_states = True
client = discord.Client(intents=intents)
bot = commands.Bot(command_prefix='`', intents=intents)




@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    for guild in client.guilds:
        print(f'     Connected to server: <{guild.name}> Members count: {len(guild.members)}')

@client.event
async def on_voice_state_update(member, before, after):
    '''DiscordPy Method called each time a user in a connected server updates their voice status
        eg. join/leave vc, deafen, mute.

            NOTES:
    member.guild.id #discord server id of the server that the user just joined
    '''
    pce = get_ptf_channel_event(before,after) #ptf channel event - custom handler
    
    #filter out non-channel changing events (mute/deafen/etc)
    if pce['status'] == 'same':
        return

    #User joined a new channel
    if pce['to'] is not None:
        pc = ptf_channel_dict[pce['to']]
        print('joined')
        pc.update(member,after)

    #User left the server - remove from previous PC
    if pce['to'] is None:
        pc = ptf_channel_dict[pce['from']]
        pc.remove(member)

    #Set update flag if the last person left the server
    if pc.get_counts() == 0:
        pc.needs_update = True
    return  


@bot.command()
async def test(ctx):
    print('test')
    for guild in client.guilds:
        print(guild.name) # prints all server's names


'''Non-Discord async Functions'''
async def ptf_timed_log(async_session,seconds):
    '''Records playing, waiting, and spectating in each channel/server every (default) 5 minutes'''
    while True:
        ptf_channel_log_count = 0
        tfp_server_log_count = 0
        failed_log_count = 0
        for ptf_channel in ptf_channel_dict.values():
            if ptf_channel.user_count() > 0:
                log = ptf_channel.log_data()
                #insert_log(log, async_session)
                stmt = ptfLogs(**log)
                async with async_session() as session:
                    try:
                        async with session.begin():
                            session.add(stmt)
                            await session.flush()
                            await session.refresh(stmt)
                            ptf_channel_log_count +=1
                    except SQLAlchemyError as e:
                        error = str(e.__cause__)
                        await session.rollback()
                        failed_log_count +=1
                        raise RuntimeError(error) from e
                    finally:
                        await session.close()
        
        for tfp_server in tf2pickup_dict.values():
            if tfp_server.user_count() > 0:
                log = tfp_server.log_data()
                #insert_log(log, async_session)
                stmt = ptfLogs(**log)
                async with async_session() as session:
                    try:
                        async with session.begin():
                            session.add(stmt)
                            await session.flush()
                            await session.refresh(stmt)
                            tfp_server_log_count += 1
                    except SQLAlchemyError as e:
                        error = str(e.__cause__)
                        await session.rollback()
                        failed_log_count +=1
                        raise RuntimeError(error) from e
                        
                    finally:
                        await session.close()
        
        if ptf_channel_log_count + tfp_server_log_count + failed_log_count > 0:
            print(f'{datetime.datetime.now()}: Logged {ptf_channel_log_count} Discord Servers and {tfp_server_log_count} TF2Pickup.org Servers  ({failed_log_count} Failed)')
        await asyncio.sleep(seconds)


    
async def ptf_timed_update(async_session,seconds):
    '''Updates servers in ptf_channel_dict and tfp_channel_dict and pushes updates to ptfChannels table every (default 60 seconds)
        Servers without an update flag are skipped'''
    while True:
        '''ptf_channel_dict'''
        for ptf_channel in ptf_channel_dict.values():
            if ptf_channel.needs_update:
                async with async_session() as session:
                    try:
                        async with session.begin():
                            stmt = sa.select(ptfChannels).where(ptfChannels.ptf_channel_id == ptf_channel.ptf_channel_id)
                            result = await session.execute(stmt)
                            a1 = result.scalars().one()
                            for k,v in ptf_channel.count_data().items():
                                setattr(a1,k,v)
                            await session.flush()
                            ptf_channel.needs_update = False
                    except SQLAlchemyError as e:
                        error = str(e.__cause__)
                        await session.rollback()
                        raise RuntimeError(error) from e
                    finally:
                        await session.close()

        '''tf2pickup_dict'''
        for tfp_server in tf2pickup_dict.values():
            if tfp_server.needs_update:
                queue = await tfp_server.get_queue()
                match = await tfp_server.get_latest_match()
                #if len(queue) > 0 or len(match) > 0:
                #    print(f'queued: {len(queue)} playing:{len(match)}')
                async with async_session() as session:
                        try:
                            async with session.begin():
                                stmt = sa.select(ptfChannels).where(ptfChannels.ptf_server_id == str(tfp_server.ptf_server_id))
                                result = await session.execute(stmt)
                                a1 = result.scalars().first()
                                counts = tfp_server.count_data()
                                for k,v in counts.items():
                                    setattr(a1,k,v)
                                await session.flush()
                                
                        except SQLAlchemyError as e:
                            error = str(e.__cause__)
                            await session.rollback()
                            raise RuntimeError(error) from e
                        finally:
                            await session.close()
            


        await asyncio.sleep(seconds)

'''Helper Functions for Discord API'''
def get_ptf_channel_event(before,after):
        '''Returns which ptf_channel_id a user came from or went to, 
            including if they moved voice channels but not pug channels'''
        
        #Check if channel changed
        if before.channel is not None and after.channel is not None:
            if before.channel.id == after.channel.id:
                return {'status':'same'}

        ptf_channel_id_from = None
        ptf_channel_id_to = None
        if before.channel:
            #try/except will also catch joining a vc that is not a pug channel
            try:
                ptf_channel_id_from = ptf_channel_lookup[before.channel.id]
            except:
                ptf_channel_id_from = None
        if after.channel:
            try:
                ptf_channel_id_to = ptf_channel_lookup[after.channel.id]
            except:
                ptf_channel_id_to = None
            #going to channel
        #if they arent the same, they switched channels withing a server
        status='within'
        if ptf_channel_id_from == ptf_channel_id_to:
            status='within'

        return {'from':ptf_channel_id_from,'to':ptf_channel_id_to,'status':status}



'''Class Definitions'''
class User:
    def __init__(self,dsc_user_id,dsc_server_id):
        self.dsc_user_id = dsc_user_id
        self.dsc_server_id = dsc_server_id
        return

class DiscordServer:
    '''DiscordServer object '''
    def __init__(self,dsc_server_id, dsc):
        return

class TF2PickupServer:
    '''TF2Pickup object conatins information for a discrete tf2pickup.org instance'''
    def __init__(self,ptf):
        '''Initialized with a ptf_servers entry'''
        self.ptf_server_name = ptf['ptf_server_name']
        self.ptf_server_id = ptf['ptf_server_id']
        self.ptf_server_status = ptf['ptf_server_status']
        self.ptf_channel_id = ptf['ptf_channel_id']
        self.tfp_api_url = f"https://api.{ptf['ptf_server_name']}"
        #https://api.tf2pickup.eu/games?limit=1
        #https://api.tf2pickup.eu/queue

        self.match_dict = {} #{'tfp_match_id':{'state':'}}
        #states = launching, started, ended

        self.playing = []
        self.waiting = []
        self.spectating = []
        self.needs_update = True #
        return
    
    def count_data(self):
        count_data = {'ptf_playing':len(self.playing),
                    'ptf_waiting':len(self.waiting),
                    'ptf_spectating':len(self.spectating)
                    }
        return count_data
    
    def user_count(self):
        return int(len(self.playing) + len(self.waiting) + len(self.spectating))

    def log_data(self):
        log_data = {'ptf_log_datetime': datetime.datetime.now(),
                    'ptf_server_id':self.ptf_server_id,
                    'ptf_channel_id':self.ptf_channel_id,
                    'ptf_playing':len(self.playing),
                    'ptf_waiting':len(self.waiting),
                    'ptf_spectating':len(self.spectating)
                    }
        return log_data
    
    async def get_latest_match(self) -> list:        
        url = urllib.parse.urljoin(self.tfp_api_url, 'games?limit=1')
        async with aiohttp.ClientSession() as session:
            tasks = []
            task = asyncio.create_task(self.get_json(session, url))
            tasks.append(task)
            
            response = await asyncio.gather(*tasks, return_exceptions=True)
            #self.waiting = []
            #Check all 'slots' to see if a player is in the slot
            try:
                tfp_match_id = response[0]['results'][0]['id']
                tfp_match_state = response[0]['results'][0]['state']

                '''
                Cases - Match is in self.match_dict
                            -state has not changed
                                -players could change
                            -state has changed

                    - Match is not in self.match_dict
                
                '''

                players = [] #keep track of players in this match, could have more matches
                for s in response[0]['results'][0]['slots']:
                    if 'player' in s.keys():
                        players.append(s['player']['steamId'])
                
                
                if tfp_match_id not in self.match_dict.keys() and tfp_match_state not in  ['ended','interrupted']:
                    #there is a new game that is currently playing
                    print(f'{tfp_match_id}: match playing - adding to dict')
                    self.match_dict[tfp_match_id] = {'state':tfp_match_state,'slots':players} #create dict entry if none exists
                    self.playing.extend(players) #add to server playing list
                elif tfp_match_state not in ['ended','interrupted']:
                    #there is an old game that is currently playing
                    self.playing = [x for x in players if x not in self.playing] #add all players that were in the match if not already added
                elif tfp_match_id in self.match_dict.keys() and tfp_match_state in  ['ended','interrupted']:
                    #there is an old game that has ended
                    self.playing = [x for x in self.playing if x not in players] #remove all players that were in the match
                    del self.match_dict[tfp_match_id]
                return self.playing
            except:
                pass
            return self.playing

    
    def get_match(self,tfp_match_id):
        match_url = f'https://{self.tfp_api_url}/games/{tfp_match_id}'
        return
    


    async def get_json(self, client: aiohttp.ClientSession, url: str) -> dict:
        async with client.request('GET', url) as response:
            response.raise_for_status()
            j = await response.json()
            return j

    async def get_queue(self, **kwargs) -> list:
        url = urllib.parse.urljoin(self.tfp_api_url, 'queue')
        async with aiohttp.ClientSession(**kwargs) as session:
            tasks = []
            task = asyncio.create_task(self.get_json(session, url))
            tasks.append(task)
            
            response = await asyncio.gather(*tasks, return_exceptions=True)
            self.waiting = []
            #Check all 'slots' to see if a player is in the slot
            try:
                for s in response[0]['slots']:
                    if 'player' in s.keys():
                        self.waiting.append(s['player']['steamId'])
                return self.waiting
            except:
                pass
            return self.waiting


class PugChannel:
    '''PugChannel object contains all information for a self-contained discord channel
            A Discord Guild (server) may contain one ore more pug channels, which often have
            differing user requirements or playstyles. 
    '''
    def __init__(self,dsc):
        #init from key value pairs (dsc) from database
        self.ptf_server_name = dsc['ptf_server_name']
        self.ptf_channel_name = dsc['ptf_channel_name']
        self.ptf_server_id = dsc['ptf_server_id']
        self.ptf_channel_id = dsc['ptf_channel_id']
        self.dsc_server_id = dsc['dsc_server_id']
        self.dsc_vc_playing = [x for x in [dsc['dsc_vc_red_a'], dsc['dsc_vc_blu_a'], dsc['dsc_vc_red_b'], dsc['dsc_vc_blu_b'], dsc['dsc_vc_red_c'], dsc['dsc_vc_blu_c']] if not None]
        self.dsc_vc_waiting = [x for x in [dsc['dsc_vc_waiting'], dsc['dsc_vc_captains'], dsc['dsc_vc_pick_next']] if not None]
        self.dsc_vc_spectating = [x for x in [dsc['dsc_vc_spectator']] if not None]
        self.dsc_vc_all = self.dsc_vc_playing + self.dsc_vc_waiting + self.dsc_vc_spectating

        self.playing = []
        self.waiting = []
        self.spectating = []
        self.needs_update = True #flag for if the PugChannel has no more players, but hasn't been updated in the database.
        return
    
    def user_count(self):
        return int(len(self.playing) + len(self.waiting) + len(self.spectating))

    def log_data(self):
        log_data = {'ptf_log_datetime': datetime.datetime.now(),
                    'ptf_server_id':self.ptf_server_id,
                    'ptf_channel_id':self.ptf_channel_id,
                    'ptf_playing':len(self.playing),
                    'ptf_waiting':len(self.waiting),
                    'ptf_spectating':len(self.spectating)
                    }
        return log_data
    
    def count_data(self):
        count_data = {'ptf_playing':len(self.playing),
                    'ptf_waiting':len(self.waiting),
                    'ptf_spectating':len(self.spectating)
                    }
        return count_data

    def remove(self, player_id):
        '''Removes a player from all lists if they are in the list'''
        if player_id in self.playing:
            self.playing.remove(player_id)
        if player_id in self.waiting:
            self.waiting.remove(player_id)
        if player_id in self.spectating:
            self.spectating.remove(player_id)

        self.needs_update = True
        return None

    def add(self, player_id, after):
        status = self.get_channel_type(after)
        if status == 'playing':
            self.playing.append(player_id)
        elif status == 'waiting':
            self.waiting.append(player_id)
        elif status == 'spectating':
            self.spectating.append(player_id)
        else:
            return
        
        self.needs_update = True
        return
    
    def update(self, player_id, after):
        '''Resets a users status using the discord channel id they move to.
            Statuses: remove, playing, waiting, specatating'''
        self.remove(player_id)
        self.add(player_id,after)
        self.needs_update = True
        return
       
    def get_channel_type(self,channel):
        '''Determine which status a dsc_channel_id should be associated with'''
        if channel.channel.id in self.dsc_vc_playing:
            #
            return 'playing'
        elif channel.channel.id in self.dsc_vc_waiting:
            #
            return 'waiting'
        elif channel.channel.id in self.dsc_vc_spectating:
            #
            return 'spectating'
        else:
            print('unexpected channel type behavior :(')
            return "none"
        
    def get_event(self, before, after):
        '''Describes the event that just occured'''
        #Get join case [jc]
        if not before.channel and after.channel:
            #Was not in any channel and joined - 
            pass


        elif before.channel and after.channel:
            #Was in a channel before joining current channel - moved
            jc = 2
        elif before.channel and not after.channel:
            #Was in a channel and disconnected
            jc = 3

    def get_counts(self):
        counts = {'server':self.ptf_server_name,'channel':self.ptf_channel_name,'playing':len(self.playing),'waiting':len(self.waiting),'spectating':len(self.spectating)}
        return counts


Base = declarative_base()
class ptfLogs(Base):
    '''SQL Table ptfLogs'''
    __tablename__ = 'ptf_logs'
    ptf_server_id = sa.Column(sa.SmallInteger, primary_key=True)
    ptf_channel_id = sa.Column(sa.SmallInteger)
    ptf_log_datetime= sa.Column(sa.DateTime(timezone=True))
    ptf_playing = sa.Column(sa.SmallInteger)
    ptf_waiting = sa.Column(sa.SmallInteger)
    ptf_spectating = sa.Column(sa.SmallInteger)

    def __init__(self, **kwargs):
        super(ptfLogs, self).__init__(**kwargs)

class ptfChannels(Base):
    '''SQL Table ptfChannels'''
    __tablename__ = 'ptf_channels'
    ptf_channel_id= sa.Column(sa.SmallInteger, primary_key=True)
    ptf_server_id= sa.Column(sa.SmallInteger)
    ptf_server_name= sa.Column(sa.String(64))
    ptf_channel_name= sa.Column(sa.String(64))
    ptf_channel_type= sa.Column(sa.SmallInteger)
    dsc_server_id= sa.Column(sa.Integer)
    dsc_channel_id= sa.Column(sa.Integer)
    dsc_tc_announcements= sa.Column(sa.Integer)
    dsc_tc_connect_info= sa.Column(sa.Integer)
    dsc_vc_spectator= sa.Column(sa.Integer)
    dsc_vc_pick_next= sa.Column(sa.Integer)
    dsc_vc_waiting= sa.Column(sa.Integer)
    dsc_vc_captains= sa.Column(sa.Integer)
    dsc_vc_misc= sa.Column(sa.Integer)
    dsc_vc_red_a= sa.Column(sa.Integer)
    dsc_vc_blu_a= sa.Column(sa.Integer)
    dsc_vc_red_b= sa.Column(sa.Integer)
    dsc_vc_blu_b= sa.Column(sa.Integer)
    dsc_vc_red_c= sa.Column(sa.Integer)
    dsc_vc_blu_c= sa.Column(sa.Integer)
    ptf_playing= sa.Column(sa.SmallInteger)
    ptf_waiting= sa.Column(sa.SmallInteger)
    ptf_spectating= sa.Column(sa.SmallInteger)

    def __init__(self, **kwargs):
        super(ptfChannels, self).__init__(**kwargs)

'''Main Program'''

'''Import Config File'''

with open("mapreview.tf/ptf_bot.cfg", "r") as stream:
    config = yaml.safe_load(stream)

'''Database'''

'''Connect to local Pug Channel Database'''
ptf_channel_dict = {}
ptf_channel_lookup = {}
ptf_users = []

ptf_non_discord_server_ids = []

tf2pickup_dict = {}



engine = create_engine(config['SQLALCHEMY_DATABASE_URI'])
session = Session(engine)
try:
    
    ex = session.execute("SELECT * FROM ptf_channels")
    k = ex.keys()
    s = ex.all()
    #print(k)
    #Add PugChannel object to channel dictionary 
    for c in s:
        kv = dict(zip(k,c)) #create dictionary from sql database keys and row values, PugChannel requires this input for init
        #kv['ptf_channel_id'] #unique key for a PugChannel
        if(kv['ptf_channel_type'] != 1):
            #skip non-discord servers
            ptf_non_discord_server_ids.append(kv['ptf_server_id'])
            continue
        ptf_channel_dict[kv['ptf_channel_id']] =  PugChannel(kv)
        for l,v in kv.items():
            if 'dsc' in l and v is not None:
                ptf_channel_lookup[v] = kv['ptf_channel_id']
    print(f'Loaded {len(ptf_channel_dict)} Discord PUG Channels')
except:
    print("ERROR: Cannot access discord channel database")
try:
    #get TF2Pickup.org instances from ptf_servers table and create TF2PickupServer objects, servers listed as dead will not be grabbed
    ex = session.execute("Select * from ptf_servers where ptf_server_name like '%tf2pickup%' and ptf_server_status != 9;")
    k = ex.keys()
    s = ex.all()
    print(ptf_non_discord_server_ids)
    for c in s:
        kv = dict(zip(k,c))
        if str(kv['ptf_server_id']) not in ptf_non_discord_server_ids:
            #add server to ptf_channels to track playercounts
            print(f"adding {kv['ptf_server_name']} to ptf_channels")
            session.add(ptfChannels(**{
                'ptf_server_id':kv['ptf_server_id'],
                'ptf_server_name':kv['ptf_server_name'],
                'ptf_channel_name':kv['ptf_server_name'],
                'ptf_channel_type':2,
                'ptf_playing':0,
                'ptf_waiting':0,
                'ptf_spectating':0
                }))
            
        session.commit()
        tf2pickup_dict[kv['ptf_server_id']] = TF2PickupServer(kv)

    #add instances to ptf_channels to track player numbers if they aren't already there
        


    print(f'Loaded {len(tf2pickup_dict)} TF2Pickup.org Instances')

    
    session.close()
except:
    print("ERROR: Cannot access TF2Pickup database")

session.close()


'''Async Database Connection'''
engine = create_async_engine(config['SQLALCHEMY_ASYNC_DATABASE_URI'])
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

async def insert_log(log, async_session: sessionmaker):
    stmt = ptfLogs(**log)
    async with async_session() as session:
        try:
            async with session.begin():
                session.add(stmt)
                await session.flush()
                await session.refresh(stmt)
        except SQLAlchemyError as e:
            error = str(e.__cause__)
            await session.rollback()
            raise RuntimeError(error) from e
        finally:
            await session.close()
    return


async def update_ptf_channel(ptf_channel_id, data, async_session: sessionmaker):
    async with async_session() as session:
        try:
            async with session.begin():
                session.query(ptfChannels).filter(ptfChannels.ptf_channel_id == ptf_channel_id).update(data)
                await session.flush()
                await session.refresh(stmt)
        except SQLAlchemyError as e:
            error = str(e.__cause__)
            await session.rollback()
            raise RuntimeError(error) from e
        finally:
            await session.close()
    return


'''Main Event Loop'''
loop = asyncio.get_event_loop() 
loop.create_task(ptf_timed_log(async_session,300))
loop.create_task(ptf_timed_update(async_session,60))

while True:
    try:
        loop.run_until_complete(client.start(config['DISCORD_BOT_TOEKN']))  # bot login with token
    except Exception as e:
        print("Error", e)  # or use proper logging
    print("Waiting until restart")
    time.sleep(10)  # sleep for 10 seconds
