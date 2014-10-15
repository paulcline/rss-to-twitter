import logging
import sqlite3
import sys
import yaml

logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO, datefmt='%Y-%m-%d %H:%M:%S')

try:

  config_file = file("config.yaml", 'r')
  config = yaml.load(config_file)

  db = sqlite3.connect(config["database"])
  cursor = db.cursor()
  
  cursor.execute("DELETE FROM recent WHERE tweetdate <= date('now', ?)", ("-%s day" % config["purge_days"],))
  logging.info("%s row(s) deleted" % cursor.rowcount)
  db.commit()  
  
  db.execute("VACUUM")
  db.commit()
  db.close()

except Exception as e:

  logging.critical(e)
  sys.exit()