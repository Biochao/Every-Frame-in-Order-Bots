# Every-Frame-in-Order-Bots
Python scripts that make and upload frames from shows to various platforms

# How to Use
1. Download and extract this repository to your machine.
2. Copy your source videos to a sources folder on your machine. Supported formats are .mkv, .mp4, and .m4v (Make sure the file names follow this convention, the dashes are important: For episodes:"Showname - #x# - Episode Title.mp4" For specials: "Showname - Special Title.mp4" Examples: "Pokemon - 1x66 - The Evolution Solution.mkv", "Pokemon - The First Movie - Mewtwo Strikes Back.mkv"
3. If using subtitles make sure they are extracted as .srt and named the same as the videos.
4. Edit makeFrames.py to set your directories and configure frame extraction. Follow the comments in the file.
5. Run makeFrames.py to extract frames from the sources directory or the source file.
6. Check the frames folders to see what will be uploaded. Delete any frames you don't want to be uploaded.
7. Make a showname folder in the facebook folder. Keep it short like one word.
8. Copy the files from the example_show_name folder to your showname folder.
9. Edit config.py to your preferred settings. You'll need to set the file config set posting speed and add your api keys to it. Follow the comments in the file.
10. If using end_post you might want to edit end_post_message in frame_uploader.py to customise the end post.




You can modify frame_uploader.py however you want if you know how. However, no support will be given if you do. I made it so almost everything can be changed using config.py.
