import glob
import gzip
import json


class DataMunger:
  def getTweetsFromSource(self, dirToSearch):
    """
    Retrieves gzipped tweet archives and imports them into a dictionary

    :param dirToSearch:
    :return:
    """
    tweetsJsonDict = {}

    # read from local files
    filesListPath = glob.glob(dirToSearch + "/*.gz")
    requestListJson = []
    for filePath in filesListPath:
      with gzip.open(filePath, 'r') as fin:
        for line in fin:
          l = line.decode("utf-8")
          l = l.strip()
          j = json.loads(l)
          requestListJson.append(j)

          # gzipFile = gzip.open(filePath)
          # content = str(gzipFile.read())
          # content = content[2:]
          # content = content[:-1]
          # filesListJSON.append(content)
          # break

    # get unique tweets
    collisions = 0
    count = 0
    for requestJson in requestListJson:
      tweets = requestJson["statuses"]
      for tweet in tweets:
        count += 1
        id = tweet["id"]
        if id not in tweetsJsonDict:
          tweetsJsonDict[id] = tweet
        else:
          collisions += 1

    return tweetsJsonDict
