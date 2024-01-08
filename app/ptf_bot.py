import discord
from discord.ext import commands

import datetime
import asyncio
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
        pc.update(member,after)

    #User left the server - remove from previous PC
    if pce['to'] is None:
        pc = ptf_channel_dict[pce['from']]
        pc.remove(member)

    print(pc.get_counts())
    return  


@bot.command()
async def test(ctx):
    print('test')
    for guild in client.guilds:
        print(guild.name) # prints all server's names


'''Non-Discord async Functions'''
async def ptf_timed_log(async_session):
    while True:
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
                    except SQLAlchemyError as e:
                        error = str(e.__cause__)
                        await session.rollback()
                        raise RuntimeError(error) from e
                    finally:
                        await session.close()
                        

        await asyncio.sleep(300)

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

    def remove(self, player_id):
        '''Removes a player from all lists if they are in the list'''
        if player_id in self.playing:
            self.playing.remove(player_id)
        if player_id in self.waiting:
            self.waiting.remove(player_id)
        if player_id in self.spectating:
            self.spectating.remove(player_id)
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
        return
    
    def update(self, player_id, after):
        '''Resets a users status using the discord channel id they move to.
            Statuses: remove, playing, waiting, specatating'''
        self.remove(player_id)
        self.add(player_id,after)
       
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

'''Main Program'''

'''Import Config File'''
with open("app\discord\ptf_bot.cfg", "r") as stream:
    config = yaml.safe_load(stream)

'''Database'''

'''Connect to local Pug Channel Database'''
ptf_channel_dict = {}
ptf_channel_lookup = {}
ptf_users = []
try:
    engine = create_engine(config['SQLALCHEMY_DATABASE_URI'])
    session = Session(engine)
    ex = session.execute("SELECT * FROM ptf_channels")
    k = ex.keys()
    s = ex.all()
    #print(k)
    #Add PugChannel object to channel dictionary 
    for c in s:
        kv = dict(zip(k,c)) #create dictionary from sql database keys and row values, PugChannel requires this input for init
        #kv['ptf_channel_id'] #unique key for a PugChannel

        ptf_channel_dict[kv['ptf_channel_id']] =  PugChannel(kv)
        for l,v in kv.items():
            if 'dsc' in l and v is not None:
                ptf_channel_lookup[v] = kv['ptf_channel_id']

    session.close()
except:
    print("ERROR: Cannot access discord channel database")

print(ptf_channel_dict)

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




'''Main Event Loop'''
loop = asyncio.get_event_loop() 
loop.create_task(ptf_timed_log(async_session))
while True:
    try:
        loop.run_until_complete(client.start(config['DISCORD_BOT_TOEKN']))  # bot login with token
    except Exception as e:
        print("Error", e)  # or use proper logging
    print("Waiting until restart")
    time.sleep(10)  # sleep for 10 seconds
