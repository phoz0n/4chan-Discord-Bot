import discord
from discord.ext import commands
import json
import urllib3
import random
import os
from discord.ext import commands, tasks
from dotenv import load_dotenv
from yandex import YandexImage

load_dotenv()
channel_id = int(os.getenv('CHANNEL'))
default_intents = discord.Intents.default()
default_intents.members = True
client = commands.Bot('!')
http = urllib3.PoolManager()
quatrechan_boards = ['3','a','aco','adv','an','b','bant','biz','c','cgl','ck','cm','co','d','diy','e','f','fa','fit','g','gd','gif','h','hc','his','hm','hr','i','ic','int','jp','k','lgbt','lit','m','mlp','mu','n','news','o','out','p','po','pol','pw','qa','qst','r','r9k','s','s4s','sci','soc','sp','t','tg','toy','trash','trv','tv','u','v','vg','vip','vm','vmg','vp','vr','vrpg','vst','vt','w','wg','wsg','wsr','x','xs','y']
useragent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:92.0) Gecko/20100101 Firefox/92.0'
accept = 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
redditModeList = ['hot', 'new', 'top', 'rising', 'random', 'controversial', 'best']
badWords = os.getenv('BADWORDS').split(",")
channel = client.get_channel(channel_id)
game = discord.Game("sending memes")


async def reddit(board, message: discord.Message):
    response = http.request('GET', 'https://www.reddit.com/r/' + board + '/random.api', headers={'User-agent':useragent} )
    data = json.loads(response.data)
    try:
        gallery = ''
        for x in data[0]['data']['children'][0]['data']['gallery_data']['items']:
            gallery = gallery + 'https://i.redd.it/' + x['media_id'] + '.jpg '
        await message.reply(gallery)
        return
    except:
        pass
    try:
        await message.reply(data[0]['data']['children'][0]['data']['title'] + ' ' + data[0]['data']['children'][0]['data']['secure_media']['reddit_video']['fallback_url'])
        return
    except:
        pass
    try:
        await message.reply(data[0]['data']['children'][0]['data']['title'] + ' ' + data[0]['data']['children'][0]['data']['url'])
    except:
        await message.reply('Not found')

async def quatrechamps(board, message: discord.Message):
    response = http.request('GET', 'https://a.4cdn.org/' + board + '/catalog.json')
    pages = json.loads(response.data)

    threads = []
    for i in pages:
        threads = threads+i["threads"]

    #Exclude threads without images
    threads_images = list(filter(lambda x: x['images'] > 0, threads))

    #Fetch a random thread from threads
    thread_pif = threads_images[random.randrange(0,len(threads_images)-1)]
    response = http.request('GET', 'https://a.4cdn.org/' + board + '/thread/' + str(thread_pif['no']) + '.json')
    thread = json.loads(response.data)
    posts = thread['posts']

    #Exclude posts without images from the random thread
    posts_images = list(filter(lambda x: 'filename' in x, posts))

    #Fetch a random post from the random thread
    post_pif = posts_images[random.randrange(0,len(posts_images)-1)]

    #Send the webm to discord channel
    await message.reply('https://is2.4chan.org/'+ board +'/' + str(post_pif['tim']) + str(post_pif['ext']))

@client.event
async def on_ready():
    print("Ready")
    await client.get_channel(channel_id).send("wesh alors")
    await client.change_presence(status=discord.Status.idle, activity=game)

@client.event
async def on_message(message: discord.Message):

    if message.author == client.user:
        return

    for i in badWords:
        if i in message.content:
            await message.reply(message.author.display_name + ' pas de ça chez nous!')
            await message.add_reaction('💩')
            return

    #4chan random img
    if message.content.lower().startswith('random'):

        #Split received words in array
        searchBoard = str(message.content).split(' ')
        if len(searchBoard) == 1:
            board = 'wsg'
        else:
            board = searchBoard[1]

        #4chan boards
        if board in quatrechan_boards:
            await quatrechamps(board,message)
            return

        #Reddit subreddits
        else:
            await reddit(board,message)
            return

    # Yandex image search
    if message.content.lower().startswith('image'):
        parser = YandexImage()
        yandexsearch = str(message.content).split(' ')
        result = parser.search(yandexsearch[1])
        randomIndex = random.randint(0, len(result)-1)
        await message.reply(result[randomIndex].url)

    # Clear section
    ctx = await client.get_context(message)
    split = message.content.split()
    if split[0] == "clear": #Checking if the message is the clear command, you can also use message.content.tolower().startswith("$clear"):
        if len(split) == 2:
            num = 0
            try:
                num = int(split[1]) #checking if the second param <amount> is an int
            except ValueError:
                await message.channel.send("<amount> in clear <amount> must be a number")
                return
            await ctx.channel.purge(limit = num)
        else:
            await message.channel.send("Please enter the command as clear <amount>")

client.run(os.getenv('TOKEN'))