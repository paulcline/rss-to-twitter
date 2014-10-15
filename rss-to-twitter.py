import feedparser
import logging
import os
import sqlite3
import sys
import twitter
import yaml

logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO, datefmt='%Y-%m-%d %H:%M:%S')

try:

  config_path = os.path.join(os.path.dirname(__file__), "config.yaml")
  config_file = file(config_path, 'r')
  config = yaml.load(config_file)

  feed = feedparser.parse(config["feed"])
  if feed.bozo == 1:
    logging.debug("Reading \"%s\": %s" % (config["feed"], feed["bozo_exception"]))

  db = sqlite3.connect(config["database"])
  
  db.execute("CREATE TABLE IF NOT EXISTS recent (url varchar(255), tweetdate TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL)")
  db.commit()
  
  cursor = db.cursor()

  twitterApi = twitter.Api(
    config["twitter"]["consumer_key"],
    config["twitter"]["consumer_secret"],
    config["twitter"]["access_token_key"],
    config["twitter"]["access_token_secret"])

  for entry in feed["entries"]:

    # check entry["link"] in database, make sure it hasn't been tweeted
    url = entry["link"]
    cursor.execute("SELECT * FROM recent WHERE url = ?", (url,))
    result = cursor.fetchone()

    if result:
      logging.info("URL \"%s\" tweeted on %s; Nothing to do." % (url, str(result[1])))
      break

    char_limit = 140

    # if url > char_limit, don't tweet (todo: bitly?)
    if len(url) > char_limit:
      logging.warning("URL: %s is too long; Consider implementing a shortener!" % (url))
      break

    # build message, if something gets truncated it should be the title
    message = "%s %s" % (entry["title"][:char_limit-1-len(url)], url)

    # insert url into database
    cursor.execute("INSERT INTO recent(url) VALUES (?)", (url,))

    db.commit()
    db.close()

    logging.info("Tweeting \"%s\" | length: %s" % (message, len(message)))

    twitterApi.PostUpdate(message)

    break

except Exception as e:

  logging.critical(e)
  sys.exit()