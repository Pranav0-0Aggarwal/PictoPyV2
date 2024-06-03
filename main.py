
import os
import sqlite3
from typing import Dict, List, Generator
from utils.fs import genHash, isImg, imgPaths
from utils.db import connectDB, createTable, executeQuery, closeConnection, hashExist
from yolov8 import detectedClass

def processImgs(conn: sqlite3.Connection, files: Generator[str, None, None]) -> None:
    for file in files:
        if not isImg(file):
            continue
        imgHash = genHash(file)
        if hashExist(conn, imgHash):
            continue
        # Add condition to check if the file path is same as the one attached to hash in DB (TBI)
        imgClass = detectedClass(file)
        query = f"INSERT OR REPLACE INTO media(hash, imageClass) VALUES('{imgHash}', '{imgClass}')"
        executeQuery(conn, query)

def fileByClass(conn: sqlite3.Connection, files: Generator[str, None, None], tableID: str) -> Dict[str, List[str]]:
    rows = executeQuery(conn, f"SELECT imageClass, hash FROM {tableID}")
    classDict = {}
    for row in rows:
        imageClass, hashValue = row
        if imageClass not in classDict:
            classDict[imageClass] = []
        filePath = detectFileWithHash(files, hashValue)
        if filePath:
            classDict[imageClass].append(filePath)
    return classDict

def classifyPath() -> Dict[str, List[str]]:
    dbPath = os.path.join(os.path.expanduser("~"), ".pictopy.db")
    columns = ["hash TEXT PRIMARY KEY", "imageClass TEXT"]
    tableID = "media"
    conn = connectDB(dbPath)
    createTable(conn, tableID, columns)

    files = imgPaths(os.path.expanduser("~"))
    processImgs(conn, files)

    result = fileByClass(conn, files, tableID)
    closeConnection(conn)

    return result

# Test case
if __name__ == "__main__":
    print(classifyPath())

# periodically run the object detection function and compare it with DB