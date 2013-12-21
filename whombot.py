import tweepy
import re, time

# Subjects and starters of subjects
subjects = [
"i", "i'm", "im", "you", "u", "you're", "youre", "he", "he's", "hes",
"she", "she's", "shes", "one", "ones", "one's", "we", "were", "we're", 
"they", "they're", "theyre,", "the", "a", "my", "your", "his", "her", 
"their", "it", "its", "it's", "ye", "thee", "thou," "thy", "thine", 
"some", "many", "several", "do", "everyone", "someone", "to", "that",
"i've", "ive", "you've", "youve", "we've", "weve", "they've", "theyve",
"i'd", "id", "you'd", "youd", "he'd", "hed", "she'd", "shed", "we'd",
"wed", "they'd", "theyd", "eva", "evar", "yu", "yew", "yoo", "this",
"dis", "that", "dat", "others", "people", "our", "uu"
]

allowed = [
"god", "jesus", "christ", "bible", "quran", "qoran", "koran", 
"cowardice", "allah", "buddha", "?", '"'
]

allowed_before = ["with", "to", "of", "for", "from", "by", "after", "against", "towards"]
allowed_after = ["ever", "eva", "evur", "evar", "of"]

corrected = set()

def setup_api():
    consumer_key = "CONSUMER_KEY"
    consumer_secret = "CONSUMER_SECRET"
    access_key = "ACCESS_KEY"
    access_secret = "ACCESS_SECRET"

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_key, access_secret)
    return tweepy.API(auth)

api = setup_api()

def get_tweets():
    tweets = api.search("whom", lang="en", max=100)
    return [(t.id_str, t.from_user,
             t.text.encode("ascii", "ignore")) for t in tweets]

def make_correction(ID, author, message):
    reply = "@%s Correction: " % author
    fixed = message.replace("&amp;", "&")
    fixed = fixed.replace("RT ", "")
    fixed = fixed.replace("whom", "WHO")
    fixed = re.sub(r"[@#]\w+:?", "", fixed).strip()
    if len(reply + fixed) > 138:
        fixed = fixed[fixed.find("WHO"):]
        if len(reply + fixed) > 138:
            fixed = " ".join(fixed[:110].split()[:-1])

    reply += '"%s"' % fixed
    print reply
    api.update_status(reply, in_reply_to_status_id=ID)

def is_incorrect(message):
    match = re.search(r"(\w+) whom (\w+)", message)
    if not match:
        return None
    before = match.group(1)
    after = match.group(2)

    return not ( any(word in message.lower() for word in allowed)
                 or after.lower() in allowed_after
                 or before.lower() in allowed_before 
                 or after.lower() in subjects 
                 or after[0].isupper()
               )

def main():
    print "Running...\n"

    while True:
        tweets = get_tweets()
        for ID, author, message in tweets:
            if is_incorrect(message) and message not in corrected:
                make_correction(ID, author, message)
                corrected.add(message)
                break
        else:
            # If no incorrect tweets were found, try again in 60 seconds
            time.sleep(60)
            continue

        time.sleep(60 * 60)

if __name__ == "__main__":
    main()
