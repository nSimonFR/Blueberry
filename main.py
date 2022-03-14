from PIL import Image, ImageDraw, ImageFont
from types import ClassMethodDescriptorType
import requests, colorgram, os
import time as t
import dbus

display = '3840x1600'.split('x')
defaultImagePath = 'ImageCache/background.jpg' # You can set your default background (relative path)

def get_song_id():
    try:
        if not hasattr(get_song_id, "session_bus"):
            get_song_id.session_bus = dbus.SessionBus()

        spotify_bus=get_song_id.session_bus.get_object("org.mpris.MediaPlayer2.spotify", "/org/mpris/MediaPlayer2")
        spotify_properties=dbus.Interface(spotify_bus, "org.freedesktop.DBus.Properties")
        metadata=spotify_properties.Get("org.mpris.MediaPlayer2.Player", "Metadata")
        status=(spotify_properties.Get("org.mpris.MediaPlayer2.Player", "PlaybackStatus"))

        if status.lower() != "playing" and status.lower() != "paused":
            return False

        track=str(metadata["xesam:title"])
        artist=str(metadata["xesam:artist"][0])
        album=str(metadata["xesam:album"])
        arturl=str(metadata["mpris:artUrl"])
        status=status.lower().capitalize()

        imageRequest = requests.get(str(arturl))
        file = open("./ImageCache/newCover.png", "wb")
        file.write(imageRequest.content)
        file.close()

        return [track, artist]
    except Exception as error:
        #print(error)
        return False

old_song_id = None
while 1:
    song_id = get_song_id()
    imagePath = False

    if old_song_id != song_id:
        old_song_id = song_id
        if not song_id:
            print('No song playing.')
            if defaultImagePath:
                print('Switching to default')
                imagePath = defaultImagePath
        else:
            print('Switching to', song_id[0], '-', song_id[1])

            # Setup Album Image
            width = int(int(display[0]) / 5)
            height = int(int(display[1]) / 2)

            baseWidth = int(display[0])
            baseHeight = int(display[1])
            image = Image.open("./ImageCache/newCover.png")
            wpercent = (width/float(image.size[0]))
            hsize = int((float(image.size[1])*float(wpercent)))
            image = image.resize((width,hsize), Image.ANTIALIAS)
            image.save('./ImageCache/albumImage.png')

            #Setup Background Colors
            colors = colorgram.extract('./ImageCache/albumImage.png', 2)
            if len(colors) < 2:
                firstColor = colors[0]
                secondColor = colors[0]
            else:
                firstColor = colors[0]
                secondColor = colors[1]

            #Create images with colors
            colorImageOne = Image.new('RGB', (baseWidth, int(baseHeight / 2)), (firstColor.rgb))
            titleArtist = ImageDraw.Draw(colorImageOne)
            songTitle = song_id[0]
            songArtist = song_id[1]
            myFont = ImageFont.truetype("./fonts/Rubik.ttf", 40)
            titleArtist.text((50,50), (songTitle + "\n" + songArtist), font = myFont, fill = (255,255,255))
            colorImageOne.save('./ImageCache/firstColor.png')

            colorImageTwo = Image.new('RGB', (baseWidth, int(baseHeight / 2)), (secondColor.rgb))
            colorImageTwo.save('./ImageCache/secondColor.png')

            #Combine Images
            background = Image.new('RGB', (colorImageOne.width, colorImageOne.height + colorImageTwo.height))
            background.paste(colorImageOne, (0, 0))
            background.paste(colorImageTwo, (0, colorImageOne.height))
            background.save('./ImageCache/background.png')

            finalImage = Image.new('RGB', (width, height))
            background.paste(image, ((int(background.width/2) - int(image.width / 2)), int((background.height/2) - int(image.height / 2))))
            background.save("./ImageCache/finalImage.png")
            imagePath = "ImageCache/finalImage.png"

        #set image
        if imagePath:
            cwd = os.getcwd()
            os.system("gsettings set org.gnome.desktop.background picture-uri " + cwd + '/' + imagePath)

    t.sleep(1)

