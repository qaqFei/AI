import sys
import zipfile
import json
import io
import typing
from os import listdir

import pydub

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

for disc in listdir(f"{sys.argv[1]}/discs"):
    for chart in listdir(f"{sys.argv[1]}/discs/{disc}"):
        chartZip = zipfile.ZipFile(f"{sys.argv[1]}/discs/{disc}/{chart}")
        name = "RIZ_" + chart[:-len(".zip")]
        
        audioSeg: pydub.AudioSegment = pydub.AudioSegment.from_ogg(io.BytesIO(findFileByExtname(chartZip, ".ogg")))
        audioSeg.export(f"./dataset/audios/{name}.ogg", format="ogg")
        
        for chartJson, diffi in zip((
            findFileByExtname(chartZip, ".json", "IN.json"),
            findFileByExtname(chartZip, ".json", "AT.json")
        ), ("IN", "AT")):
            if chartJson is None: continue
            chartJson = json.loads(chartJson)
            
            totalSec = 0
            bpmData = []
            for i, e in enumerate(chartJson["bpmShifts"]):
                if i > 0:
                    totalSec += 60 / (chartJson["bpmShifts"][i - 1]["value"] * chartJson["bPM"]) * (e["time"] - chartJson["bpmShifts"][i - 1]["time"])
                    
                bpmData.append({
                    "startTime": totalSec,
                    "bpm": e["value"] * chartJson["bPM"]
                })
            
            def beat2sec(t: float):
                sec = 0.0
                for i, e in enumerate(chartJson["bpmShifts"]):
                    bpm = e["value"] * chartJson["bPM"]
                    if i != len(chartJson["bpmShifts"]) - 1:
                        et_beat = chartJson["bpmShifts"][i + 1]["time"] - e["time"]
                        
                        if t >= et_beat:
                            sec += et_beat * (60 / bpm)
                            t -= et_beat
                        else:
                            sec += t * (60 / bpm)
                            break
                    else:
                        sec += t * (60 / bpm)
                        
                return sec
                
            picksoundData = set()
            
            for line in chartJson["lines"]:
                for note in line["notes"]:
                    picksoundData.add(beat2sec(note["time"]))
            
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
