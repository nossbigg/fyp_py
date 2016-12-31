import sys
sys.path.append('../')

from controller import DataMunger as DM

# import controller.DataMunger

x = DM.DataMunger()
z = x.f()

print(z)
filesPath = x.getFiles("C:\\Users\\Gibson\\adbpull\\data\\gib-tweet-fyp\\#sickhillary")
print(len(filesPath))
print(filesPath[0])

content = x.readGzipFile(filesPath[0])
print(content)

