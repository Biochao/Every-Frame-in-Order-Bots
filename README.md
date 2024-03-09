# Every-Frame-in-Order-Bots
Python scripts that make and upload frames from shows to various platforms

# Features
• Simple to use and edit

• Frame extractor script makes frames for every video in a folder or just one video file

• Makes info files while extracting frames

• Visual indication of what and how many frames will be uploaded

• Upload bot can report errors and status to Discord

• Configureable timings for post batches and amount

• Can retry on errors for a number of times before giving up

• Support for adding subtitles with a configurable font and style to frames from .srt files

• Option to increment a counter when ever a specific word or phrase in a subtitle

• Can log post ids it uploads

• Configurable random comments on posts

• Option to upload images to an album during or at the end of an episode



# How to Use
1. Have a Facebook Page and api keys follow this guide on how to get them https://github.com/boidushya/FrameBot/blob/master/generateToken.md
2. Download and extract this repository to your machine.
3. Copy your source videos to a sources folder on your machine. Supported formats are .mkv, .mp4, and .m4v (Make sure the file names follow this convention, the dashes are important: For episodes:"Showname - #x# - Episode Title.mp4" For specials: "Showname - Special Title.mp4" Examples: "Pokemon - 1x66 - The Evolution Solution.mkv", "Pokemon - The First Movie - Mewtwo Strikes Back.mkv"
4. If using subtitles make sure they are extracted as .srt and named the same as the videos.
5. Edit makeFrames.py to set your directories and configure frame extraction. Follow the comments in the file.
6. Run makeFrames.py to extract frames from the sources directory or the source file.
7. Check the frames folders to see what will be uploaded. Delete any frames you don't want to be uploaded.
8. Make a showname folder in the facebook folder. Keep it short like one word.
9. Copy the files from the example_show_name folder to your showname folder.
10. Edit config.py to your preferred settings. You'll need to set the file config set posting speed and add your api keys to it. Follow the comments in the file.
11. If using end_post you might want to edit end_post_message in frame_uploader.py to customise the end post.
12. Run frame_uploader to start posting frames!




You can modify frame_uploader.py however you want if you know how. However, no support will be given if you do. I made it so almost everything can be changed using config.py.
