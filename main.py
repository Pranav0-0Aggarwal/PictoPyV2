import os
import sqlite3
from typing import Dict, List, Generator
from utils import *
from media import *
from yolov8 import detectClasses
from flask import Flask, render_template, send_file, request, redirect, url_for
from markupsafe import escape


def dbPath() -> str:
    """
    Database is created on the user's home directory.

    Returns:
        str: The path to the database file.
    """
    directory = os.path.join(os.path.expanduser("~"), ".pictopy")
    os.makedirs(directory, exist_ok=True)
    return os.path.join(directory, "database.db")

def processMedia(conn: sqlite3.Connection, files: Generator[str, None, None]) -> None:
    """
    Processes files by extracting their hash values.
    If hash already exists in the database, just update the path.
    Otherwise detect classes and insert them into the database.

    Args:
        conn: The database connection object.
        files: A generator of file paths.
    """
    
    objDetectionModel = pathOf("models/yolov8n.onnx")
    for file, fileType, parentDir in files:
        fileHash = genHash(file)
        if updateMediaPath(conn, file, fileHash):
            continue
        try:
            if fileType == "vid":
                mediaClass = videoClasses(file, objDetectionModel)
            elif fileType == "img":
                mediaClass = imageClasses(file, objDetectionModel)
        except Exception as e:
            print(e)
            continue
        insertIntoDB(conn, mediaClass, fileHash, file, fileType)

def classifyPath(hidden, fileType) -> Dict[str, List[str]]:
    """
    Classify files in the home directory and store the results in the database.

    Returns:
        Dict[str, List[str]]: Dictionary mapping class names to lists of file paths.
    """
    conn = connectDB(dbPath())
    createSchema(conn, 
        {
            "MEDIA": [
                "mediaID INTEGER PRIMARY KEY AUTOINCREMENT", 
                "hash TEXT UNIQUE", 
                "path TEXT UNIQUE",
                "fileType TEXT CHECK(fileType IN ('img', 'vid'))",
                "hidden INTEGER"
            ],
            "CLASS": [
                "classID INTEGER PRIMARY KEY AUTOINCREMENT", 
                "class TEXT UNIQUE"
            ],
            "JUNCTION": [
                "mediaID INTEGER", 
                "classID INTEGER", 
                "FOREIGN KEY(mediaID) REFERENCES MEDIA(mediaID) ON DELETE CASCADE",
                "FOREIGN KEY(classID) REFERENCES CLASS(classID)",
                "PRIMARY KEY (mediaID, classID)"
            ]
        }
    )

    processMedia(conn, mediaPaths(homeDir()))

    # Clear unavailable paths from DB
    cleanDB(conn)

    result = groupByClass(conn, hidden, fileType)

    closeConnection(conn)

    return result

app = Flask(__name__, template_folder=f"{pathOf('static')}")

@app.route('/')
def index():
    return redirect(url_for('groupMedia', fileType='img', groupBy='classes'))

@app.route('/static/<path:path>')
def staticFile(path):
    return app.send_static_file(pathOf(path))

@app.route('/media/<path:path>')
def sendFile(path):
    path = escape(f"/{path}")
    if pathExist(path):
        return send_file(path)
    return redirect(url_for('index')) # doesn't reload (TBI)

# Sections

@app.route('/<string:fileType>/<string:groupBy>')
def groupMedia(fileType, groupBy):
    if fileType not in ["img", "vid"]:
        return redirect(url_for('index'))
    return render_template('index.html', classDict=classifyPath(0, fileType))

@app.route('/hidden/<string:groupBy>')
def hidden(groupBy):
    return render_template('index.html', classDict=classifyPath(1, "any"))

@app.route('/trash/<string:groupBy>')
def trash(groupBy):
    return render_template('index.html', classDict=classifyPath(1, "any")) # 1 instead of -1 for demo (TBI)

# Buttons

@app.route('/delete', methods=['POST'])
def delete():
    data = request.get_json().get('selectedMedia', [])
    print(f"Deleting files: {data}")
    conn = connectDB(dbPath())
    deleteFromDB(conn, data)
    closeConnection(conn)
    return redirect(url_for('index'))

@app.route('/hide', methods=['POST'])
def hide():
    data = request.get_json().get('selectedMedia', [])
    print(f"Hiding files: {data}")
    conn = connectDB(dbPath())
    toggleVisibility(conn, data, 1)
    closeConnection(conn)
    return redirect(url_for('index'))

@app.route('/info/<path:path>')
def info(path):
    return os.stat(path)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
