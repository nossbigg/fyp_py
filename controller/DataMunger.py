import sys, glob, gzip, json

sys.path.append('../')


class DataMunger:
  workingDir = ""

  def __init__(self, workingDir):
    self.workingDir = workingDir

  def getTweetsFromSource(self, dirToSearch):
    tweetsJsonList = {}

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
    for requestJson in requestListJson:
      tweets = requestJson["statuses"]
      for tweet in tweets:
        id = tweet["id"]
        if id not in tweetsJsonList:
          tweetsJsonList[id] = tweet
        else:
          collisions += 1

    return tweetsJsonList
