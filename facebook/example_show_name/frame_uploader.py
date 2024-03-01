import pysrt
from PIL import Image, ImageDraw, ImageFont
import requests
import discord
from discord import Webhook, RequestsWebhookAdapter, File
from io import BytesIO
import os
import re
import json
import sys
import time
import datetime
import random
import config

def make_post():
    # URL format and fields are according to facebook's API documentation
    # Since no API version is explicitly given in the link, requests will always use the latest API version
    url = (
        f"https://graph.facebook.com/{config.page_id}/photos?"
        f"caption={status_text}&access_token={config.access_token}"
    )
    # Check if the frame is a file path or a PIL image
    if isinstance(frame, str):
        # Open the image using PIL if a file path is provided
        image = Image.open(frame_path)
    else:
        image = frame

    # Convert the image to bytes
    image_bytes = BytesIO()
    image.save(image_bytes, format="JPEG")
    image_data = image_bytes.getvalue()

    files = {'file': ('frame.jpg', image_data, 'image/jpeg')}
        
    # Send http POST request to /page-id/photos to make the post
    response = requests.post(url, files=files)
    
    # Check the status code
    if response.status_code == 200:
        # Successful request
        return response.json()
    elif response.status_code == 400:
        # Bad request, handle accordingly
        return response.json()
    elif response.status_code == 401:
        # Unauthorized, handle accordingly
        return response.json()
    elif response.status_code == 403:
        # Forbidden, handle accordingly
        return response.json()
    elif response.status_code == 404:
        # Not found, handle accordingly
        return response.json()
    elif response.status_code == 368:
        # Facebook abuse
        print("Facebook thinks spam abuse!")
        if config.connect_to_discord:
            webhook.send(f"Facebook thinks posts are spam! Stopping the {config.bot_name}.")
            input("Press Enter to resume...")
        return response.json()
    else:
        # Handle other status codes here
        return response.json()
    
def make_album_post():
    # URL format and fields are according to facebook's API documentation
    # Since no API version is explicitly given in the link, requests will always use the latest API version
    url = (
        f"https://graph.facebook.com/{album_id}/photos?"
        f"caption={post_text}{album_status}&access_token={config.access_token}"
    )
    files = {
        'image': open(file_path, "rb")
    }
    # Send http POST request to /album-id/photos to add the frame in the album
    response = requests.post(url, files=files)
    # Check the status code
    if response.status_code == 200:
        # Successful request
        return response.json()
    elif response.status_code == 400:
        # Bad request, handle accordingly
        return response.json()
    elif response.status_code == 401:
        # Unauthorized, handle accordingly
        return response.json()
    elif response.status_code == 403:
        # Forbidden, handle accordingly
        return response.json()
    elif response.status_code == 404:
        # Not found, handle accordingly
        return response.json()
    elif response.status_code == 368:
        # Facebook abuse
        print("Facebook thinks spam abuse!")
        if config.connect_to_discord:
            webhook.send(f"Facebook thinks posts are spam! Stopping the {config.bot_name}.")
            input("Press Enter to resume...")
        return response.json()
    else:
        # Handle other status codes here
        return response.json()

def make_comment():
    # make request to add comment to post
    print(f"Adding comment to post {post_id}")
    comment_url = f"https://graph.facebook.com/{post_id}/comments?access_token={config.access_token}&message={comment_message}"
    response = requests.post(comment_url)
    return response.json()
    if response.status_code == 200:
        print("Comment added successfully!")
    else:
        print(f"Failed to add comment. Error: {response.json}")

def open_image(image_path_or_obj):
    if isinstance(image_path_or_obj, Image.Image):
        return image_path_or_obj
    else:
        return Image.open(image_path_or_obj)

def read_json(file_path):
    try:
        # Open the file in read mode
        with open(file_path, 'r') as json_file:
            # Load the JSON data from the file
            data = json.load(json_file)
            print("Loaded JSON file")

            # Return the loaded data
            return data.get("Video Info")

    except json.JSONDecodeError as e:
        print(f"Error decoding JSON in file {file_path}: {e}")
        return None
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return None

def save_frame(show_name, frame, season_number, episode_number, frame_index, timestamp):
    # Build output folders from video info
    if regular_episode:
        debug_folder = os.path.join(config.debug_output_folder, show_name, f"s{season_number}e{episode_number}")
    else:
        debug_folder = os.path.join(config.debug_output_folder, show_name, video_name)
    
    # Create the output folders if they don't exist
    os.makedirs(config.debug_output_folder, exist_ok=True)
    os.makedirs(os.path.join(config.debug_output_folder, show_name), exist_ok=True)
    os.makedirs(debug_folder, exist_ok=True)
    # Save the frame as an image in the output folder
    output_filename = os.path.join(debug_folder, f"{timestamp:08d}.jpg")
    print(f"DEBUG: Saving current frame to {output_filename}")
    frame.save(output_filename, quality=50)

def save_sub_frame(show_name, frame, season_number, episode_number, frame_index, timestamp):
    # Build output folders from video info
    if regular_episode:
        debug_folder = os.path.join(config.debug_output_folder, show_name, f"s{season_number}e{episode_number}_sub")
    else:
        debug_folder = os.path.join(config.debug_output_folder, show_name, video_name+"_sub")
    
    # Create the output folders if they don't exist
    os.makedirs(config.debug_output_folder, exist_ok=True)
    os.makedirs(os.path.join(config.debug_output_folder, show_name), exist_ok=True)
    os.makedirs(debug_folder, exist_ok=True)
    # Save the frame as an image in the output folder
    output_filename = os.path.join(debug_folder, f"{timestamp:08d}.jpg")
    print(f"DEBUG: Saving current frame to {output_filename}")
    frame.save(output_filename, quality=50)

def timestamp_format(milliseconds):
    seconds, milliseconds = divmod(milliseconds, 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)

    return "{:02}:{:02}:{:02}.{:03}".format(int(hours), int(minutes), int(seconds), int(milliseconds))

def convert_to_unix_path(windows_path):
    # Replace backslashes with forward slashes
    unix_path = windows_path.replace("\\", "/")
    
    return unix_path

def log_to_file(log_file_path, new_entry):
    try:
        # Read existing data from the file
        if os.path.exists(log_file_path):
            with open(log_file_path, 'r') as json_file:
                data = json.load(json_file)
        else:
            # If the file doesn't exist, initialize data as an empty list
            data = []

        # Append the new entry to the existing data
        data.append(new_entry)

        # Write the updated data back to the file
        with open(log_file_path, 'w') as json_file:
            json.dump(data, json_file, indent=2)

        print(f"Post logged to {log_file_path}")

    except json.JSONDecodeError as e:
        print(f"Error decoding JSON in file {log_file_path}: {e}")
    except Exception as e:
        print(f"Error processing file {log_file_path}: {e}")

# Initialize and test credentials
if config.online_mode:
    try:
        url = f"https://graph.facebook.com/{config.page_id}"
        params = {
            "access_token": config.access_token,
            "fields": "name"
        }
        response = requests.get(url, params=params)
        page_name = response.json()["name"]
        print(f"Connected to Facebook page {page_name}")
    except:
        print("Facebook not OK, trying again in 60 seconds")
        for e in sys.exc_info():
            print(e)
        time.sleep(60)

if config.connect_to_discord:
    webhook = Webhook.partial(config.webhook_id, config.discord_webhook_token, adapter=RequestsWebhookAdapter())
    
# Create logs subfolder if it doesn't exist
if config.logging:
    logs_folder = 'logs'
    if not os.path.exists(logs_folder):
        os.makedirs(logs_folder)
        print("Created logs folder!")

# Load the counters from a file
if config.use_counters:
    counter1 = config.counter1_file
    if os.path.exists(counter1):
        with open(counter1) as c1:
            counter1_count = int(c1.read())
        print(f"Next {config.counter1_name} count is {counter1_count}")
    else:
        counter1_count = 1
        print(f"No {config.counter1_name} counter file found. Initializing")
        with open('counter1.txt', 'w') as c1:
            c1.write(str(counter1_count))


# Read a text file to get a list of videos to go through
video_list = "video_list.txt"

# Start of episode loop
while True:
    if os.path.exists(video_list):
        print("Video list found. Reading lines.")
        with open(video_list, "r") as vl:
            video_lines = vl.readlines()
            if not video_lines:
                print("The video list file is empty.")
                break
    else:
        print("No video list file found. Creating... Replace lines with video pathnames")
        with open(video_list, "w") as vl:
            vl.write("Replace this with video pathnames")
            break

    video_path = video_lines[0].strip()
    print(f"Current Video file: {video_path}")

    # Split filename from path
    vidpath, video_file = os.path.split(video_path)
    path_without_extension, _ = os.path.splitext(video_path)
    # Split filename from extension
    video_name, video_extension = os.path.splitext(video_file)
    print(video_name)
    # Extract Info from info json file
    video_info_file = path_without_extension + ".json"
    video_info = read_json(video_info_file)
    if video_info is not None:
        show_name = video_info.get("Show Name")
        alt_show_name = video_info.get("Alt Show Name")
        season_number = video_info.get("Season Number")
        episode_number = video_info.get("Episode Number")
        title = video_info.get("Title")
        alt_title = video_info.get("Alt Title")
        regular_episode = video_info.get("Regular Episode")
        frames_folder = video_info.get("Frames Path")
        sub_frames_folder = video_info.get("Sub Frames Path")

        print(f"Show Name: {show_name}")
        print(f"Alt Show Name: {alt_show_name}")
        print(f"Season Number: {season_number}")
        print(f"Episode Number: {episode_number}")
        print(f"Title: {title}")
        print(f"Alt Title: {alt_title}")
        print(f"Regular Episode: {regular_episode}")
        print(f"Frames Path: {frames_folder}")
        print(f"Sub Frames Path: {sub_frames_folder}")
        print()
    else:
        print("Couldn't read json file")
        
    # Use alt names if they exist
    if alt_show_name:
        show_name = alt_show_name
    if alt_title:
        title = alt_title
    if season_number:
        season_number = int(season_number)
    if episode_number:
        episode_number = int(episode_number)
    # Set up the post_text
    if regular_episode: 
        post_text = f"{show_name} - {'' if config.hide_season else 'Season ' + str(season_number)+' '}Episode {episode_number} - {title}"
        print(f"Post text will look like this:\n{post_text}")
    else:
        post_text = f"{video_name}"
        print(f"Post text will look like this:\n{post_text}")
    
    # Find subtitles
    if config.use_subtitles:
        srt_path = os.path.join(path_without_extension+".srt")
        print(f"Looking for a subtitle file at {srt_path}")
        if os.path.exists(srt_path):
            # Parse the SRT subtitle file
            print("SRT file found!")
            subs = pysrt.open(srt_path)
            use_subtitles = True
        else:
            input("Can't find the srt file, press enter to continue without subtitles")
            use_subtitles = False
            
    # Configure frames folder using video info
    if sub_frames_folder:
        frames_folder = sub_frames_folder
        add_subtitles = False
    else:
        add_subtitles = True
    print(f"Frames folder set to {frames_folder}")

    # Set up the panorama location if enabled
    if config.panoramas_mix or config.panoramas_end:
        if regular_episode:
            panorama_folder = os.path.join(config.base_panoramas_folder, show_name, f"s{season_number}e{episode_number}pano")
        else:
            panorama_folder = os.path.join(config.base_panoramas_folder, show_name, video_name+"_pano")
        
        if os.path.exists(panorama_folder):
            pano_list = os.listdir(panorama_folder)
            pano_list_length = len(pano_list)
        else:
            input(f"The panorama_folder {panorama_folder} could not be found! Press any key to continue with panoramas turned off.")
            config.panoramas_mix = False
            config.panoramas_end = False

    # Determine how many frames there are
    # Get a list of all files in the folder
    all_files = os.listdir(frames_folder)
    # Filter only image files based on the file extensions
    frame_files = [frame for frame in all_files if frame.endswith(('.jpg', '.png', '.gif'))]
    list_length = len(frame_files)
    print(list_length, "files found")
    if list_length < 1:
        input('There are no frames in this folder. Press any key to continue.')

    # Load the episode progress from file (or initialize it to 0 if the file doesn't exist)
    progress_file = "progress.txt"
    if os.path.exists(progress_file):
        print("Progress file found. Resuming.")
        with open(progress_file, "r") as pf:
            frame_index = int(pf.read())
        print(f"Current Frame Index:{frame_index}")
    else:
        print("No progress file found. Starting from the beginning")
        # Initialize Episode Progress Variable
        frame_index = 0
    
    # Setting list
    print("About to start with these settings:")
    if config.online_mode:
        print("Online mode is on!")
    if config.debug_mode:
        print("Debug mode is on! Frames will be saved.")
    if config.logging:
        print("Logging is on!")
    print(f"Bot will wait {config.delay} seconds after each post")
    print(f"Bot will post {config.group} posts before waiting {config.wait_time} seconds.")
    print(f"Bot will wait {config.error_delay} seconds after an error.")
    print(f"Bot will try {config.retry_attempts} times before giving up and exiting.")
    if config.connect_to_discord:
        print("Bot will report to Discord")
    
    # Confirmation to start episode
    if config.confirmation or config.special_confirm and not regular_episode:
        input("Press enter to start the episode.")
    else:
        print("Waiting 30 seconds before starting to confirm settings.")
        time.sleep(30)

    # Report how long this episode will run for
    remaining_posts = list_length - frame_index
    runtime_seconds = remaining_posts * (config.wait_time + (config.group * (config.delay + 5))) / config.group
    runtime = datetime.timedelta(seconds = runtime_seconds)
    time_length_hours = round(runtime_seconds / 3600, 1)
    endtime = datetime.datetime.now() + runtime
    endtime_minute_only = endtime.strftime("%Y-%m-%d %H:%M")
    
    # Calculate the estimated time to the end of the series
    if regular_episode:
        episodes_left = config.num_of_eps - (int(episode_number) + config.previous_seasons_episodes)
        series_time_years = round(time_length_hours * episodes_left / 24 / 365, 1)
        series_time_months = round(time_length_hours * episodes_left / 24 / 30, 1)
        if series_time_years < 1:
            series_time_left = f"{series_time_months} months"
        else:
            series_time_left = f"{series_time_years} years"
    
    print(f"Running for {time_length_hours} hours")
    print(f"EndTime: {endtime}")
    if config.connect_to_discord:
        if frame_index == 0:
            webhook.send(f"{config.bot_name} started {post_text} Running until {endtime_minute_only}")
        else:
            webhook.send(f"{config.bot_name} resuming at frame {frame_index+1} Running until {endtime_minute_only}")

    if config.online_mode and config.start_post:
        if frame_index == 0:
            if regular_episode:
                post_message = f"{config.bot_name_short} starting new episode {post_text} \nEstimated running time {time_length_hours} hours. End time: {endtime_minute_only} EDT\n\nThere are {episodes_left} regular episodes left. If all remaining episodes are like this one it will take at least {series_time_left} to finish."
            else:
                post_message = f"{config.bot_name_short} starting new special {post_text} \nEstimated running time {time_length_hours} hours. End time: {endtime_minute_only} EDT"
            
            post_url = f"https://graph.facebook.com/me/feed?message={post_message}&access_token={config.access_token}"
            response = requests.post(post_url)

            # check the response status code
            if response.status_code == 200:
                print("Post created successfully!")
            else:
                print(f"Failed to create post. Status code: {response.status_code}")

    # Set the group index
    group_index = 0
    # Set the comment_spacing index
    comment_spacing = 0

    #Initialize optional variables for logging
    caption = ""
    
    # Process each image in the folder starting from the saved index
    for i, frame in enumerate(frame_files):
        # Skip files before the saved index
        if i < frame_index:
            continue
        frame_path = os.path.join(frames_folder, frame)
        # Split the extension from the filename
        base_frame_name, file_extension = os.path.splitext(frame)
        print(f"Reading frame {frame_index+1} of {list_length}")
        # Get the timestamp of the current frame in milliseconds
        timestamp = int(base_frame_name)
        print(f"Timestamp: {timestamp} milliseconds")
        
        # Convert the timestamp to hh:mm:ss
        formatted_timestamp = timestamp_format(timestamp).rstrip('0').rstrip('.')
        timestamp_status = f"\n\nTimestamp: {formatted_timestamp}"
        
        # Add subtitles to frame
        if use_subtitles:
            # Find the subtitle that corresponds to the specified timestamp
            if timestamp > 0:
                caption = subs.at(timestamp)
                caption = caption.text
            else:
                caption = ""
                
            if add_subtitles:
                # Create a PIL image
                frame = open_image(frame_path)
                draw = ImageDraw.Draw(frame)
                width, height = frame.size
                
                # Remove tags like italics from the caption. PIL and most sites don't support them
                # Remove <i>
                caption = caption.replace("<i>", "")
                # Remove </i>
                caption = caption.replace("</i>", "")

                # Load the TTF font settings from the config
                # Calculate maximum font size based on percentage of image height
                max_font_size = int(height * config.max_font_percentage)
                font_size = max_font_size
                custom_font = ImageFont.truetype(config.font_path, font_size)
                fill = config.fill_color
                stroke_width = config.stroke_width
                stroke_fill = config.stroke_fill
                alignment = config.alignment

                # Get the size of the caption text
                bbLeft, bbTop, bbRight, bbBottom = draw.textbbox((0,0), caption, font=custom_font)
                
                if config.debug_mode:
                    print(bbLeft, bbTop, bbRight, bbBottom)
                
                text_width = bbRight - bbLeft
                text_height = bbBottom - bbTop
                
                if config.debug_mode:
                    print(text_width, text_height)
                
                # Maximum allowed width for the caption
                max_caption_width = width - 2 * int(width * config.side_margin)
                
                # Scale font size based on image size
                while text_width > max_caption_width or text_height > height:
                    font_size -= 1
                    custom_font = ImageFont.truetype(config.font_path, font_size)
                    bbLeft, bbTop, bbRight, bbBottom = draw.textbbox((0, 0), caption, font=custom_font)
                    text_width = bbRight - bbLeft
                    text_height = bbBottom - bbTop

                # Calculate position to center the text
                text_x = (width - text_width) / 2
                text_y = height - text_height - int(height * config.bottom_margin)
                
                if config.debug_mode:
                    print(text_x, text_y)

                # Add the caption to the PIL image using the custom font
                draw.text((text_x, text_y), caption, fill=fill, font=custom_font, stroke_width=stroke_width, stroke_fill=stroke_fill, align=alignment)
                
                # If debug mode is on frames that were to be uploaded will be saved to a debug folder
                if config.debug_mode:
                    save_sub_frame(show_name, frame, season_number, episode_number, frame_index, timestamp)
            
        # Prepare a status
        # Check if any forbidden word is in the caption
        forbidden = False
        if config.censor_post:
            for word in config.forbidden_words:
                if word in caption:
                    print("This caption contains a forbidden word.")
                    forbidden = True
                    break
        
        caption_status = "Caption: "    
        if use_subtitles and not forbidden:
            status_text = f"{post_text}\nFrame {frame_index+1}/{list_length}\n{caption_status if caption else ''}{caption if caption else ''}"
            if config.post_timestamps:
                status_text += f"\n{timestamp_status}"
            if config.use_hashtags:
                # Add hashtags from config file
                separator = " "
                hashtags = separator.join(config.hashtags)
                status_text += f"\n{hashtags}"
                # Add season/episode number hashtags
                if regular_episode:
                    status_text += f" #s{season_number}e{episode_number}" 
        else:
            status_text = f"{post_text}\nFrame {frame_index+1}/{list_length}"
            if config.post_timestamps:
                status_text += f"\n{timestamp_status}"
            if config.use_hashtags:
                separator = " "
                hashtags = separator.join(config.hashtags)
                status_text += f"\n{hashtags}"
                # Add season/episode number hashtags
                if regular_episode:
                    status_text += f" #s{season_number}e{episode_number}"
        
        print(status_text)
        
        if config.online_mode:
            # Upload the frame
            retries = 0
            success = False
            while not success and retries < config.retry_attempts:
                try:
                    post_response = make_post()
                    upload_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    if config.logging:
                        if post_response.get('id'):
                            post_id = post_response['post_id']
                            frame_path = convert_to_unix_path(frame_path)
                            video_path = convert_to_unix_path(video_path)
                            if regular_episode:
                                log_filename = f"s{season_number}e{episode_number}_log.json"
                            else:
                                log_filename = f"special_{video_name}_log.json"
                            log_file_path = os.path.join(logs_folder, log_filename)
                            
                            new_entry = {
                                "Post ID": post_id,
                                "Post Info": {
                                    "Post Text": post_text,
                                    "Frame Index": frame_index,
                                    "Caption": caption,
                                    "Timestamp": timestamp,
                                    "Frame Path": frame_path,
                                    "Source Video": video_path,
                                    "Upload Time": upload_time 
                                }
                            }
                            log_to_file(log_file_path, new_entry)
                    print(f"---> Post done! Time: {upload_time}")
                    post_id = post_response["post_id"]
                    
                    # Add a comment if phrase in caption only if 30 posts have passed
                    if config.use_counters:
                        # Copy this if statment and change counter# to add more counters
                        if config.counter1_phrase in caption.lower() and comment_spacing > config.min_comment_spacing:
                            print(f"Waiting {config.comment_delay} seconds to make comment!")
                            time.sleep(config.comment_delay)
                            comment_message = f"{config.comment_message_prefix}{counter1_count} times! -{config.bot_name_short}"
                            comment_response = make_comment()
                            comment_spacing = 0
                            counter1_count += 1
                            # Save progress to text file
                            with open(counter1, "w") as b:
                                b.write(str(counter1_count))
                        comment_spacing += 1
                            
                    # Add a comment at random
                    if config.random_comments:
                        if random.random() < config.probability and comment_spacing > config.min_comment_spacing:
                            comment_message = random.choice(config.random_comment_list)
                            # Append the bot name at the end of the comment
                            comment_message += f" -{config.bot_name_short}"
                            print("Randomly chose to make a comment:", comment_message)
                            time.sleep(config.comment_delay)
                            comment_response = make_comment()
                    
                    # Upload a panorama if there is one with the same name as the frame
                    if config.panoramas_mix:
                        if base_frame_name in pano_list:
                            print("Matching Panorama found! Waiting to upload!")
                            time.sleep(30)
                            file_path = os.path.join(panorama_folder, base_frame_name+file_extension)
                            pano_list_index = pano_list.index(base_frame_name)
                            album_id = config.panoramas_album_id
                            album_status = f"\nPanorama {pano_list_index+1} of {pano_list_length}"
                            post_response = make_album_post()
                    
                    success = True
                except:
                    print(f'Error while posting image {frame_path}')
                    for e in sys.exc_info():
                        print(e)
                    retries += 1
                    print(f"Trying again in {config.error_delay} seconds.")
                    time.sleep(config.error_delay)
            if not success:
                print(f'Failed to post image {base_frame_name}{file_extension} after {retries} attempts')
                for e in sys.exc_info():
                                    print(e)
                if config.connect_to_discord:
                    webhook.send(f"{config.bot_name} failed to post image {base_frame_name}{file_extension} after {retries} attempts.")
                # Wait for user input before exiting
                input("Too many errors. Press any key to restart...")
        else:
            print(f"Processing file {base_frame_name}{file_extension}")
            # Simulate comment if phrase in caption only if 30 posts have passed
            if config.use_counters:
                print(f"Comment spacing is {comment_spacing}")
                if config.counter1_phrase in caption.lower() and comment_spacing > config.min_comment_spacing:
                    comment_message = f"{config.comment_message_prefix}{counter1_count} times! -{config.bot_name_short}"
                    print(f"Phrase found! {comment_message}")
                    time.sleep(30)
                    comment_spacing = 0
                    counter1_count += 1
                comment_spacing += 1
            # If using subtitles and debug mode is on, output what will be uploaded to a folder for testing
            if use_subtitles:
                if config.debug_mode:
                    save_frame(show_name, frame, season_number, episode_number, frame_index, timestamp)
        print("")
        
        # Increment frame
        frame_index = frame_index+1
        
        # Save Progress
        with open(progress_file, "w") as pf:
                pf.write(str(frame_index))
        
        # If the group index has reached the specified amount, sleep for the specified wait time before resetting the counter and continuing to post the next batch of frames
        group_index += 1
        if group_index < config.group:
            print(f"Waiting for {config.delay} seconds\n")
            time.sleep(config.delay) # Time in between each post
        else:
            print(f"Group done!")
            print(f"Waiting for {config.wait_time} seconds\n")
            time.sleep(config.wait_time) # Time in between each batch of posts
            group_index = 0
            

    # Add last image without caption to the To Be Continued album
    if config.toBeContinued and regular_episode and config.online_mode:
        album_id = config.toBeContinued_album_id
        album_status = "\nTo Be Continued..."
        file_path = os.path.join(frames_folder, frame_files[-1])
        post_response = make_album_post()
        print("To be continued added to album. Waiting to upload panoramas")
        time.sleep(config.wait_time/2)

    if config.panoramas_end:
        print("Uploading panoramas!")
        album_id = config.panoramas_album_id
        for filename in pano_list:
            file_path = os.path.join(panorama_folder, filename)
            pano_list_index = pano_list.index(filename)
            album_status = f"\nPanorama {pano_list_index+1} of {pano_list_length}"
            post_response = make_album_post()
            time.sleep(145)
        print("All panoramas uploaded")
    
    # Stats
    total_frames_file = "total_frames.txt"
    if os.path.exists(total_frames_file):
        print("Stats file found. Reading.")
        with open(total_frames_file, "r") as tf:
            total_frames = int(tf.read())
            current_total = total_frames + list_length
        
        # Save new total to text file
        with open("total_frames.txt", "w") as tf:
            tf.write(str(current_total))
    else:
        print("No stats file found. Creating...")
        with open(total_frames_file, "w") as tf:
            tf.write("0")
            
        with open(total_frames_file, "r") as tf:
            total_frames = int(tf.read())
            current_total = total_frames + list_length
        
        # Save new total to text file
        with open("total_frames.txt", "w") as tf:
            tf.write(str(current_total))

    
    if config.end_post:
        # Self Promotion ending
        promo_file = "../../promos.txt" # Create it 2 directories up so all bots can share it
        if os.path.exists(promo_file):
            print("Promotions file found. Reading.")
            with open(promo_file, 'r') as urls:
                lines = urls.readlines()
        else:
            print("No promotions file found. Creating... Add urls to it!")
            with open(promo_file, "w") as urls:
                urls.write("URL")

        random_url = random.choice(lines)

        end_post_message = f"{config.end_post_phrase}\n \nThis is a fan run page. The posts may be automated but it takes a lot of time to process the frames for the bot. If you'd like to support me check out my Redbubble for fan-made designs on shirts, stickers and more!\nHere's a random one: {random_url} \n \nI also have a Youtube channel where I remake Pokemon cutscenes in 3D animations. https://www.youtube.com/c/Biochao \n\nOr if you just want to give a little tip you can do so here: https://ko-fi.com/biochao \n\nStats:\nPosted {current_total} frames since starting the page."
        
        if config.online_mode:
            
            post_url = f"https://graph.facebook.com/me/feed?message={end_post_message}&access_token={config.access_token}"
            response = requests.post(post_url)

            # check the response status code
            if response.status_code == 200:
                print("Post created successfully!")
            else:
                print(f"Failed to create post. Status code: {response.status_code}")


    # Delete the progress file since the episode is done
    os.remove(progress_file)
    # Remove the episode from the video list
    video_lines = video_lines[1:]
    # Write the modified lines back to the video list file
    with open(video_list, 'w') as vl:
        vl.writelines(video_lines)
    
    if config.connect_to_discord:
        webhook.send(f"{config.bot_name} finished {post_text}.")
    
    print(f"Waiting for {config.wait_time/2} seconds before going to next episode.")    
    time.sleep(config.wait_time/2) # Waiting some more before going to a new episode
    
# The episode loop will exit when there are no lines remaining in the video list file
print("No more lines in the video list file.")
if config.connect_to_discord:
        webhook.send(f"{config.bot_name} ran out out of videos.")
