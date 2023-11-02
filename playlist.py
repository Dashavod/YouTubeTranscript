from pytube import Playlist
p = Playlist('https://youtube.com/playlist?list=PLfQhCXyy6psEMCeMbh3dE5jyGe9PaoY0b&si=XNbnSP6u-Nu7Cezj')
for url in p.video_urls[:3]:
    print(url)