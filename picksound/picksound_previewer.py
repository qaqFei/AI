import os
import sys
import json

current = os.path.abspath(".")
petdir = input("")
if not petdir:
    petdir = os.path.abspath("./../../phispler-ext/src")

os.chdir(petdir)
sys.path.insert(0, petdir)

os.environ["NO_FIX_WORKPATH"] = ""
import dxsmixer # type: ignore
import dxsound # type: ignore

picksound_name = input("picksound name: ")
dataset = json.load(open(f"{current}/dataset/dataset.json", "r", encoding="utf-8"))

for i in dataset["picksound"]:
    if i["dataFile"] == picksound_name:
        picksound = i
        break
else:
    print("picksound not found")
    exit()

data = json.load(open(f"{current}/dataset/{picksound["dataFile"]}", "r", encoding="utf-8"))
current_index = -1
sfx = dxsound.directSound("./resources/milres/hit.ogg")
dxsmixer.mixer.music.load(f"{current}/dataset/{picksound["soundFile"]}")
dxsmixer.mixer.music.play()
while not dxsmixer.mixer.music.get_busy():
    pass

while dxsmixer.mixer.music.get_busy():
    t = dxsmixer.mixer.music.get_pos()
    if current_index + 1 < len(data) and data[current_index + 1] <= t:
        current_index += 1
        print("at", data[current_index])
        sfx.play()
