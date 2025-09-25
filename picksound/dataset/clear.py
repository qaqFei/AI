import os
import json

if input("Sure?").lower() != "yes":
    exit()

with open("./dataset.json", "w", encoding="utf-8") as f:
    json.dump({
        "bpm": [],
        "picksound": []
    }, f, indent=4, ensure_ascii=False)

def clearDir(dirPath: str):
    for fn in os.listdir(dirPath):
        os.remove(os.path.join(dirPath, fn))
    
clearDir("./audios")
clearDir("./datas/bpm")
clearDir("./datas/picksound")
