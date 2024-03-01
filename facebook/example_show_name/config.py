# Testing Config
online_mode = True
debug_mode = False # Output what the bot is uploading to files

# Bot config
bot_name = "ExampleShowname Facebook Bot" # Used in bot reports
bot_name_short = "ExampleShowname Bot" # Used for posts and replies
confirmation = False # Wait for input to start each episode
special_confirm = False # Wait for confirmation when a special is about to start. Only use if regular confirm is off.
hide_season = False # If the show only has 1 season no need to put it in posts
logging = True # Required to use the comment bot
retry_attempts = 5 # Number of times to retry after an error uploading
random_comments = True
probability = 0.01 # Percent chance the bot will make a comment after each post
# When the bot chooses to make a comment it will choose from this list at random and sign the comment with the bot_name_short.
random_comment_list = ["How about a random comment?", "Add more random comments to the config!"] 

# API Config
page_id = 1234567890
access_token = "facebook_api_access_token_goes_here"
toBeContinued_album_id = 1
panoramas_album_id = 1

# Timing Config
delay = 60 # Seconds inbetween each post
wait_time = 1800 # Seconds after a group of posts
group = 5 # How many posts per group
error_delay = 300 # How many seconds to wait after an error

# Testing timings
if not online_mode:
    delay = 5 
    wait_time = 10

# Discord Config
connect_to_discord = True
webhook_id = 1234567890 # Channel id for bot reports
discord_webhook_token = "your_discord_webhook_token"

# Post Config
start_post = True # Make a post before uploading that has some stats
toBeContinued = False # Add last frame of episodes to a to be continued album
end_post = True # Make a post at the end of an episode. Edit message in main bot script
end_post_phrase = "To be continued..." # First line of the end post
post_timestamps = True # Add timestamps formatted to hh:mm:ss:ms to the post descriptions
censor_post = True # Don't add the caption to the post description if it contains certain words
# List of words or phrases that may get a facebook page into trouble.
forbidden_words = ["kill", "shit"]
use_hashtags = False # Only for Twitter/Mastodon
hashtags = ["#cartoon"] # Set hashtags. Procedural hashtags for seaason/episode number will be added by the bot after these

# Panoramas
panoramas_mix = False # Upload panoramas in time with the frames. Name panorama files the same as corresponding frame.
panoramas_end = False # Upload panoramas at the end of the episode
panoramas_delay = 145 # Number of seconds to wait after each panorama upload. Only for panoramas_end

# Show Config
num_of_eps = 100 # Total number of episodes in a series for calculating series end time in start_post
previous_seasons_episodes = 0 # Used for series time left. Add the number of the previous seasons episodes count

# File Config
base_panoramas_folder = r"C:/Users/framebot/bots2/panoramas"
debug_output_folder = r"C:/Users/framebot/bots2/debugFrames"

# Subtitle Config
use_subtitles = True # Add subtitles to the frames
font_path = r"C:\Windows\Fonts\arial.ttf" # Make sure the font has special characters like []:♪()
max_font_percentage = 0.07 # Percentage of the image height the caption will take up
fill_color = (255, 255, 255) # RGB Values
stroke_width = 2
stroke_fill = (0, 0, 0)
alignment = "center"
side_margin = 0.05 # Offset from sides of the frame in percent of frame width
bottom_margin = 0.03 # Offset from bottom of the frame in percent of frame height

# Counters
use_counters = False # Can only be used if subtitles are on. Will make a comment when the phrase shows up in the captions
counter1_name = "name"
counter1_file = "counter.txt"
counter1_phrase = "phrase"
min_comment_spacing = 20 # Number of posts to wait before making another comment
comment_delay = 30 # Seconds to wait before making a comment on a post
comment_message_prefix = "Counter count is " #{count} times!
