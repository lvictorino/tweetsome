import twitter
import random
import pickle
import os
import sys
import json
import datetime
import config


def file_path(desired_file):
    script_dir = os.path.dirname(__file__)
    path = os.path.join(script_dir, desired_file)
    return path


print("Gathering saved data...")
try:
    with open(file_path(config.SAVE_FILE), "r") as f:
        saved_data = json.load(f)
    print("Success.")
except (FileNotFoundError, json.decoder.JSONDecodeError):
    print("None were found. Using default data.")
    saved_data = {}
    saved_data["picked"] = []
    saved_data["last_tweet_id"] = config.DEFAULT_ROOT_ID

print("Gathering wholesome content...")
try:
    content = []
    with open(file_path(config.WHOLESOME_CONTENT), "r") as f:
        content = f.read().splitlines()
        random_tweet = random.choice(content)
        tweet_content = f"{random_tweet} {config.WHOLESOME_CONTENT}"
        print("Success.")
except FileNotFoundError:
    print("Unable to retrieve wholesome content.")
    print("Shutting down.")
    sys.exit(1)

api = twitter.Api(
    consumer_key=config.TWITAPI_CONSUMER_KEY,
    consumer_secret=config.TWITAPI_CONSUMER_SECRET,
    access_token_key=config.TWITAPI_TOKEN_KEY,
    access_token_secret=config.TWITAPI_TOKEN_SECRET,
)

print("Connecting to Twitter API...")
try:
    followers = api.GetFollowerIDs(user_id=config.TWITTER_ID)
    print("Success.\nUpdating follower cache...")
    with open(file_path(config.FOLLOWER_CACHE), "wb") as f:
        pickle.dump(followers, f, protocol=pickle.HIGHEST_PROTOCOL)
    print("Success:", len(followers), "followers.")
except twitter.error.TwitterError:
    print("Unable to connect.")

print("Getting cache...")
try:
    with open(file_path(config.FOLLOWER_CACHE), "rb") as f:
        followers_load = pickle.load(f)
except (FileNotFoundError, EOFError):
    print("Cache not found.")
    print("Shutting down.")
    sys.exit(1)

remaining_followers = set(followers_load) - set(saved_data["picked"])

if not remaining_followers:
    print("All followers have already received the wholesomeness they deserved.")
    print("Shutting down.")
    sys.exit(0)

picked_id = random.choice(followers_load)
print("Picked follower id:", picked_id)

try:
    saved_data["picked"].append(picked_id)
    picked_user = api.GetUser(user_id=picked_id)
    print(f"Getting user name: @{picked_user.screen_name}")
    tweet = f"@{picked_user.screen_name} {tweet_content}"
    print("Building tweet:", tweet)
    print("Sending tweet...")
    new_tweet = api.PostUpdate(tweet, in_reply_to_status_id=saved_data["last_tweet_id"])
    saved_data["last_tweet_id"] = new_tweet.id_str
    print("Success.")
except twitter.error.TwitterError:
    print("Unable to send a tweet.")
    print("Shutting down.")
    sys.exit(1)

print("Saving data...")
try:
    saved_data["time"] = str(datetime.datetime.now())
    with open(file_path(config.SAVE_FILE), "w") as f:
        json.dump(saved_data, f)
    print("Success.")
except (FileNotFoundError, json.decoder.JSONDecodeError):
    print("Unable to save data.")
    print("Shutting down.")
    sys.exit(1)
print("Wholesomeness has been successfully spread.")
