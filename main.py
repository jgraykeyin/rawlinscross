import tweepy as tw
import datetime
import boto3
import os

# Get the current date
today = datetime.date.today()

# Establish a connection to AWS S3
s3 = boto3.resource("s3")
bucket = s3.Bucket("rawlinscross")

# Set file location to current directory
__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

def create_new_html(days,status,date):
    html = open(os.path.join(__location__, "index.html"), "w+")

    html.write('<!DOCTYPE html><html lang="en-us"><head><link rel="preconnect" href="https://fonts.gstatic.com"><link href="https://fonts.googleapis.com/css2?family=Josefin+Sans:ital,wght@0,300;0,400;0,500;0,700;1,300&display=swap" rel="stylesheet"><title>Rawlins Cross Status</title><meta name="viewport" content="width=device-width, initial-scale=1.0"></head>')
    html.write('<link rel="stylesheet" href="styles.css"><body><div class="header"><h4 align="center">Has there been an accident on Rawlin&#39s Cross today?</h4></div>')
    if status == "no":
        html.write('<div class="answer"><h1 align="center">NO</h1></div>')
    elif status == "yes":
        html.write('<div class="answer"><h1 align="center">YES</h1></div>')
    html.write('<div class="count"><h3 align="center">{} days since last accident</h3><p align="center">Updated: {}</p></div></body></html>'.format(days,date))

    html.close()

    # Upload the HTML file
    bucket.upload_file(os.path.join(__location__, "index.html"), "index.html", ExtraArgs={'ACL': 'public-read', 'ContentType': 'text/html'})


# Open the data file to get the day-count info
f = open(os.path.join(__location__, "daycount.txt"), "r")
current_days = int(f.readline())
zero_date = f.readline()
if "\n" in zero_date:
    zero_date = zero_date.strip("\n")
f.close()

print("{} days since last accident".format(current_days))

consumer_key = os.environ.get('CONSUMER_KEY')
consumer_secret = os.environ.get('CONSUMER_SECRET')
access_token = os.environ.get('ACCESS_TOKEN')
access_token_secret = os.environ.get('ACCESS_TOKEN_SECRET')

auth = tw.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tw.API(auth, wait_on_rate_limit=True)

# Define the search term and the date_since date as variables
search_words = "#nltraffic rawlins accident"
new_search = search_words + " -filter:retweets"

# Collect tweets
tweets = tw.Cursor(api.search,
              q=new_search,
              lang="en",
              since=today).items(5)
all_tweets = []
for tweet in tweets:
    #print(tweet.created_at)
    data={"text":tweet.text, "date":tweet.created_at}
    all_tweets.append(data)

incident=0
if all_tweets:
    for tweet in all_tweets:
        #print(tweet["date"])
        #print(tweet["text"])
        incident += 1

print("Was there an accident on Rawlin's Cross today?")
if incident > 0:
    print("YES")

    if current_days > 0:
        current_days = 0
        f = open(os.path.join(__location__, "daycount.txt"), "w")
        f.write(str(current_days)+"\n")
        f.write(str(today))
        f.close()

        # Create new HTML file with updated day-count
        create_new_html(current_days, "yes", today)

else:
    print("NO")

    if str(zero_date) != str(today):
        # Increment the day-count for no accidents
        current_days += 1
        f = open(os.path.join(__location__, "daycount.txt"), "w")
        f.write(str(current_days)+"\n")
        f.write(str(today))
        f.close()

        # Create new HTML file with updated day-count
        create_new_html(current_days, "no", today)
