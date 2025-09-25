import sys
import zipfile
import json
import io
import typing
from os import listdir

import pydub

from const import *

if len(sys.argv) < 2:
    print("<unpack-folder>")
    exit()

with open("./dataset/dataset.json", "r", encoding="utf-8") as f:
    dataset: dict[str, list] = json.load(f)

def findFileByExtname(z: zipfile.ZipFile, e: str, endswith: typing.Optional[str] = None):
    for file in z.namelist():
        if file.endswith(e):
            if endswith is None or file.endswith(endswith):
                return z.read(file)
    return None

def countFileByExtname(z: zipfile.ZipFile, e: str):
    return sum(1 for file in z.namelist() if file.endswith(e))

for chart in listdir(f"{sys.argv[1]}/Packed"):
    chartZip = zipfile.ZipFile(f"{sys.argv[1]}/Packed/{chart}")
    if countFileByExtname(chartZip, ".ogg") != 1: continue
    name = "MIL_" + chart[:-len(".zip")]
        
    audioSeg: pydub.AudioSegment = pydub.AudioSegment.from_ogg(io.BytesIO(findFileByExtname(chartZip, ".ogg"))).set_frame_rate(SAMPLE_RATE)
    audioSeg.export(f"./dataset/audios/{name}.mp3", format="ogg")
        
    for chartJson, diffi in zip((
        findFileByExtname(chartZip, ".json", "Cloudburst.json"),
        findFileByExtname(chartZip, ".json", "Clear.json"),
        findFileByExtname(chartZip, ".json", "Special.json")
    ), ("Cloudburst", "Clear", "Special")):
            if chartJson is None: continue
            chartJson = json.loads(chartJson)
            
            totalSec = 0
            if "bpms" not in chartJson:
                continue
            
            offset = chartJson["bpms"][0]["start"]
            bpmData = list(filter(lambda x: x["startTime"] >= 0, map(lambda x: {
                "startTime": x["start"] - offset,
                "bpm": x["bpm"]
            }, chartJson["bpms"])))
                
            picksoundData = set()
            
            for line in chartJson["lines"]:
                for note in line["notes"]:
                    if note["isFake"]: continue
                    picksoundData.add(note["startTime"] + offset)
                
            picksoundData = sorted(list(picksoundData))
                
            with open(f"./dataset/datas/bpm/{name}_{diffi}.json", "w", encoding="utf-8") as f:
                json.dump(bpmData, f, ensure_ascii=False, indent=4)

            with open(f"./dataset/datas/picksound/{name}_{diffi}.json", "w", encoding="utf-8") as f:
                json.dump(picksoundData, f, ensure_ascii=False, indent=4)
                
                dataset["bpm"].append({
                "soundFile": f"audios/{name}.ogg",
                "dataFile": f"datas/bpm/{name}_{diffi}.json"
                })
                
            dataset["picksound"].append({
                "soundFile": f"audios/{name}.ogg",
                "dataFile": f"datas/picksound/{name}_{diffi}.json"
                })
                
            print(f"Done {name}_{diffi}")

with open("./dataset/dataset.json", "w", encoding="utf-8") as f:
    json.dump(dataset, f, ensure_ascii=False, indent=4)
