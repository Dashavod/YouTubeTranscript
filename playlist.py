from pytube import Playlist, YouTube

playlist = 'https://youtube.com/playlist?list=PLfQhCXyy6psEMCeMbh3dE5jyGe9PaoY0b&si=XNbnSP6u-Nu7Cezj'
p = Playlist(playlist)
for url in p.video_urls[:3]:
    print(url)

yt = YouTube(playlist)
title = yt.title
author = yt.author
metadata = yt.metadata
desc = yt.description
print('desc: ', author)