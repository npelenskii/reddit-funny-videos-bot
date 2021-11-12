import asyncio
import os

import asyncpraw
import http3
import youtube_dl

from hidden import reddit, headers


async def findvideo(key_word):

    x = 0

    subreddit = await reddit.subreddit("funnyvideos", fetch=True)
    
    async for submission in subreddit.new(limit=100):
        if x == 1:
            break
        if submission.link_flair_text == key_word:
            id = str(submission.id)
            print(id)
            async with http3.AsyncClient() as client:
                res = await client.get('https://www.reddit.com/r/funnyvideos/comments/'+id+'.json', headers=headers)
                res = res.json()
                for post in res:
                    data = post['data']['children']
                    for media_data in data:
                        if str(media_data['data']).find('reddit_video') != -1:
                            
                            video_url = str(media_data['data']["media"]['reddit_video']['fallback_url'])
                            video_name = str(key_word).replace('/', ' ')
                            
                            if x == 0:
                                handle = os.listdir(os.getcwd())
                                for i in handle:
                                    if i == video_name+'.mp4':
                                        os.remove(i)
                                x = x + 1
                                ydl_opts = {'outtmpl': f'{video_name}', 'format': 'bestvideo + bestaudio'}
                                with youtube_dl.YoutubeDL(ydl_opts) as ydl: 
                                    ydl.download([video_url])
                            break
