import sys
import zipfile
import json
import io
import os
from os import listdir

import pydub

if len(sys.argv) < 2:
    print("<unpack-folder>")
    exit()

with open("./dataset/dataset.json", "r", encoding="utf-8") as f:
    dataset: dict[str, list] = json.load(f)

def findFileByExtname(z: zipfile.ZipFile, e: str):
    for file in z.namelist():
        if file.endswith(e):
            return z.read(file)
    return None

for chart in listdir(f"{sys.argv[1]}/packed"):
    if chart.endswith(("EZ.zip", "HD.zip", "Legacy.zip")): continue
    chartZip = zipfile.ZipFile(f"{sys.argv[1]}/packed/{chart}")
    name = "PHI_" + chart[:-len(".zip")]
    
    audioName = name[:-3]
    audioPath = f"./dataset/audios/{audioName}.ogg"
    if not os.path.exists(audioPath):
        audioSeg: pydub.AudioSegment = pydub.AudioSegment.from_ogg(io.BytesIO(findFileByExtname(chartZip, ".ogg")))
        audioSeg.export(audioPath, format="ogg")
    
    chartJson = json.loads(findFileByExtname(chartZip, ".json"))
    bpmData = [{ "startTime": 0, "bpm": chartJson["judgeLineList"][0]["bpm"] }]
    picksoundData = set()
    
    for line in chartJson["judgeLineList"]:
        for note in line["notesAbove"] + line["notesBelow"]:
            picksoundData.add(note["time"] * 1.875 / line["bpm"] - chartJson["offset"])
    
    picksoundData = sorted(list(picksoundData))
    
    with open(f"./dataset/datas/bpm/{name}.json", "w", encoding="utf-8") as f:
        json.dump(bpmData, f, ensure_ascii=False, indent=4)

    with open(f"./dataset/datas/picksound/{name}.json", "w", encoding="utf-8") as f:
        json.dump(picksoundData, f, ensure_ascii=False, indent=4)
    
    dataset["bpm"].append({
        "soundFile": f"audios/{audioName}.ogg",
        "dataFile": f"datas/bpm/{name}.json"
    })
    
    dataset["picksound"].append({
        "soundFile": f"audios/{audioName}.ogg",
        "dataFile": f"datas/picksound/{name}.json"
    })
    
    print(f"Done {name}")

with open("./dataset/dataset.json", "w", encoding="utf-8") as f:
    json.dump(dataset, f, ensure_ascii=False, indent=4)
