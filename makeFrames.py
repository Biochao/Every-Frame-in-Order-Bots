import os
import re
import json
import subprocess


episode_info = True # Generate an info json file for each video
encode = True # Turn off to just create episode info if frames already exist

# Set the path to the folder containing the videos or a single video file
sources = r"C:\Users\framebot\bots2\sources\ExampleShowName\Season 1"

# Options to set alt names for show and episode titles
alt_show_name = "" # Option to set an alt show name to be shorter or if it has special characters in it that can't be in pathnames
alt_names_file = "episode_titles.txt" # If the episodes have alt names have this file in the source dir with the names to use

# Set the path to the folder where you want to save the frames, folders for each show will be created here with each source inside
base_frames_folder = r"C:\Users\framebot\bots2\frames"

make_pano_dirs = False # Make show folder for panoramas. Turn on if planning to make panoramas for this show
base_panos_folder = r"C:\Users\framebot\bots2\panoramas"

# Output file options 
burn_subs_copy = False # Copy of frames that have the subtitles burned in. Only use if subs are stylized or have positional data
output_names = "%08d.jpg" # this sets 0 padding to up to 8
fps = 4 # FPS the frames would play at if made into a video with the same length
quality = 5 # Higher numbers = smaller file size but more compression artifacts. 7 is around the max before artifacting

# Crop settings
# Warning! This applies the same crop to every video. If the videos need different crops put them in different folders or don't enable  this and edit the json later
crop = False # Turn on and set parameters if there are black bars on the video
crop_w = 0 # Width of the final image
crop_h = 0 # Height of the final image
crop_x = 0 # X-coordinate adjustment of the top-left corner of the final image
crop_y = 0 # Y-coordinate adjustment of the top-left corner of the final image

# Pixel Aspect Ratio Correction
pixel_aspect_ratio = 1 # Normal = 1 NTSC = 0.91 PAL = 1.09

# Set the starting index if partially completed and no progress file was made
start_index = 0

def process_video_files(sources, base_frames_folder, base_panos_folder, start_index, make_pano_dirs, burn_subs_copy, encode, episode_info):

    def convert_to_unix_path(windows_path):
        # Replace backslashes with forward slashes
        unix_path = windows_path.replace("\\", "/")
        
        return unix_path

    def remove_special_characters(file):
        # Replace single quotes with underscores
        return file.replace("'", "_").replace(",", "_")
        
    def make_info_file(info_file_path, video_info):
        try:
            # Write the updated data back to the file
            with open(info_file_path, 'w') as json_file:
                json.dump(data, json_file, indent=2)

            print(f"Video info saved to {info_file_path}")

        except json.JSONDecodeError as e:
            print(f"Error decoding JSON in file {info_file_path}: {e}")
        except Exception as e:
            print(f"Error processing file {info_file_path}: {e}")

    def find_matching_pattern(file_name):
        patterns = [
            match_episode_with_season,
            match_movie,
            match_episode_without_season,
        ]

        for pattern_function in patterns:
            match = pattern_function(file_name)
            if match:
                return match

        return None

    def match_episode_with_season(file_name):
        pattern = r'^(.+) (\d+)x(\d+) - (.+)$'
        print("Testing season and episode")
        return re.match(pattern, file_name)

    def match_episode_without_season(file_name):
        pattern = r'^(.+) - (\d+) - (.+)$'
        print("Testing episode without season")
        return re.match(pattern, file_name)

    def match_movie(file_name):
        pattern = r'^(.+?) - (.+)$'
        print("Testing movie")
        return re.match(pattern, file_name)

    def process_match(match):
        if match:
            groups = match.groups()
            if len(groups) == 4:
                show_name, season_number, episode_number, title = groups
                # Remove dashes and whitespace from values
                show_name = show_name.strip(' -')
                print("Show Name:", show_name)
                print("Season Number:", season_number if season_number else "None")
                print("Episode Number:", episode_number if episode_number else "None")
                print("Title:", title)
                print()
                return show_name, season_number, episode_number, title
            elif len(groups) == 2:
                show_name, title = groups
                # Remove dashes and whitespace from values
                show_name = show_name.strip(' -')
                print("Show Name:", show_name)
                print("Season Number: None (Special)")
                print("Episode Number: None (Special)")
                print("Title:", title)
                print()
                return show_name, None, None, title
            if season_number and not episode_number:
                season_number = 1 # If an episode number was found but no season number it was probably a single season show
        else:
            print("The file name does not match any expected pattern.")
            print()

    if os.path.isfile(sources):  # Check if sources is a file
        file_list = [os.path.basename(sources)]
        sources = os.path.dirname(sources)
    elif os.path.isdir(sources):  # Check if sources is a directory
        file_list = os.listdir(sources)
    else:
        raise ValueError("Invalid sources path provided.")

    index_file = os.path.join(sources, "progress.txt")
    if os.path.exists(index_file):
        with open(index_file) as f:
            index = int(f.read())
        print("Progress file found. Resuming.")
    else:
        index = start_index
        print("No index file found. Starting from the beginning")

    extensions = [".mkv", ".mp4", ".m4v"]
    
    for i, file in enumerate(file_list[index:], start=index):
        if file.endswith(tuple(extensions)):
            print(index + 1)
            video_path = os.path.join(sources, file)
            file_name, file_ext = os.path.splitext(file)
            show_name, season_number, episode_number, title = process_match(find_matching_pattern(file_name))

            os.makedirs(os.path.join(base_frames_folder, show_name), exist_ok=True)

            if make_pano_dirs:
                os.makedirs(os.path.join(base_panos_folder, show_name), exist_ok=True)
                os.makedirs(os.path.join(base_panos_folder, show_name, "season" + season_number), exist_ok=True)

            regular_episode = season_number is not None and episode_number is not None

            if regular_episode:
                frames_folder = f"s{season_number}e{episode_number}"
                print(f"Making episode folder {frames_folder}")
                print("Setting output folder to episode")
                output_folder = os.path.join(base_frames_folder, show_name, "season" + season_number)
            else:
                frames_folder = file_name
                print(f"Making episode folder {frames_folder}")
                print("Setting output folder to specials")
                output_folder = os.path.join(base_frames_folder, show_name, "specials")

            os.makedirs(os.path.join(output_folder, frames_folder), exist_ok=True)
            frames_path = os.path.join(output_folder, frames_folder)
            frames_path = convert_to_unix_path(frames_path)

            if burn_subs_copy:
                sub_frames_path = frames_path + "_sub"
                os.makedirs(os.path.join(output_folder, sub_frames_path), exist_ok=True)
            else:
                sub_frames_path = ""

            if os.path.isfile(os.path.join(sources, alt_names_file)) and regular_episode:
                with open(os.path.join(sources, alt_names_file), "r") as t:
                    episode_titles = t.readlines()
                    alt_title = episode_titles[int(episode_number)-1].strip()
            else:
                alt_title = ""

            if episode_info:
                print("Making episode info json file")
                episode_info_file = os.path.join(sources, f"{file_name}.json")
                data = {
                    "Video Info": {
                        "Show Name": show_name,
                        "Alt Show Name": alt_show_name,
                        "Season Number": season_number,
                        "Episode Number": episode_number,
                        "Title": title,
                        "Alt Title": alt_title,
                        "Frame Rate": fps,
                        "Regular Episode": regular_episode,
                        "Frames Path": frames_path,
                        "Sub Frames Path": sub_frames_path,
                        "Source Video": convert_to_unix_path(video_path),
                        "Crop": crop,
                        "Crop Width": crop_w,
                        "Crop Height": crop_h,
                        "Crop X": crop_x,
                        "Crop Y": crop_y
                    }
                }
                make_info_file(episode_info_file, data)

            if crop:
                crop_command = f",crop={crop_w}:{crop_h}:{crop_x}:{crop_y}"
            else:
                crop_command = ""
            scale_filter = f',scale=iw*sar:ih,setsar={pixel_aspect_ratio}'
            
            
            # Create a temporary filename without single quotes
            temp_filename = remove_special_characters(file)
            
            if burn_subs_copy:
                subtitles_filter = f'subtitles={temp_filename}'
                command = [
                    "ffmpeg", 
                    "-copyts", 
                    "-i", f"{temp_filename}", 
                    "-r", "1000", 
                    "-vf",f'fps=fps={fps},{subtitles_filter},{crop_command},{scale_filter}', 
                    "-frame_pts", "true", 
                    "-vsync", "vfr", 
                    "-q:v", f"{quality}", 
                    os.path.join(sub_frames_path, output_names), 
                    "-r", "1000", 
                    "-vf", f"fps=fps={fps}{crop_command}{scale_filter}", 
                    "-frame_pts", "true", 
                    "-vsync", "vfr", 
                    "-q:v", f"{quality}", 
                    os.path.join(frames_path, output_names)
                ]
            else:
                command = [
                    "ffmpeg", 
                    "-copyts", 
                    "-i", temp_filename,
                    "-r", "1000", 
                    "-vf", f"scale=iw*sar:ih, setsar={pixel_aspect_ratio},fps=fps={fps}{crop_command}", 
                    "-frame_pts", "true", 
                    "-vsync", "vfr", 
                    "-q:v", f"{quality}", 
                    os.path.join(frames_path, output_names)
                ]

            if encode:
                os.chdir(sources)
                
                
                print(f"Processing {file}")
                try:
                    # Rename the file to the temporary filename
                    os.rename(file, temp_filename)
                    # Open the subprocess
                    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

                    # Capture the output and error streams
                    output, error = process.communicate()

                    # Check the return code
                    if process.returncode == 0:
                        print("FFMPEG encode completed successfully.")
                    else:
                        print(f"FFMPEG encode failed with error code {process.returncode}")
                        print("Error output:\n", error)
                        input("Press enter to continue.")
                except Exception as e:
                    print("An error occurred:", str(e))
                finally:
                    # Restore the original filename
                    os.rename(temp_filename, file)

            index += 1
            with open(index_file, "w") as f:
                f.write(str(index))

    os.remove(index_file)

process_video_files(sources, base_frames_folder, base_panos_folder, start_index, make_pano_dirs, burn_subs_copy, encode, episode_info)
