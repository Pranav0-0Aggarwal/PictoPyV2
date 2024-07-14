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

def processImgs(conn: sqlite3.Connection, files: Generator[str, None, None]) -> None:
    """
    Processes images by extracting their hash values.
    If hash already exists in the database, just update the path.
    Otherwise detect classes and insert them into the database.

    Args:
        conn: The database connection object.
        files: A generator of file paths.
    """
    
    objDetectionModel = pathOf("models/yolov8n.onnx")
    for file in files:
        imgHash = genHash(file)
        if updateMediaPath(conn, file, imgHash):
            continue
        try:
            imgClass = imageClasses(file, objDetectionModel)
        except Exception as e:
            print(e)
            continue
        insertIntoDB(conn, file, imgClass, imgHash)

def classifyPath() -> Dict[str, List[str]]:
    """
    Classify images in the home directory and store the results in the database.

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
                "format TEXT CHECK(format IN ('img', 'vid'))",
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

    processImgs(conn, imgPaths(homeDir()))

    # Clear unavailable paths from DB
    cleanDB(conn)

    result = groupByClass(conn)

    closeConnection(conn)

    return result

app = Flask(__name__, template_folder=f"{pathOf('static')}")

@app.route('/')
def index():
    return render_template('index.html', classDict=classifyPath())

@app.route('/static/<path:path>')
def staticFile(path):
    return app.send_static_file(pathOf(path))

@app.route('/media/<path:path>')
def media(path):
    path = escape(f"/{path}")
    if pathExist(path):
        return send_file(path)
    return redirect(url_for('index')) # doesn't reload / (TBI)

# Sections with Demo return

@app.route('/<string:format>/<string:groupOf>')
def groupBy(format, groupOf):
    if format not in ["img", "vid"]:
        return redirect(url_for('index'))
    return render_template('index.html', classDict=classifyPath())

@app.route('/hidden/<string:groupOf>')
def hidden(groupOf):
    return render_template('index.html', classDict=classifyPath())

@app.route('/trash/<string:groupOf>')
def trash(groupOf):
    return render_template('index.html', classDict=classifyPath())

# Buttons

@app.route('/delete', methods=['POST'])
def delete():
    data = request.get_json().get('selectedMedia', [])
    print(f"Deleting images: {data}")
    conn = connectDB(dbPath())
    deleteFromDB(conn, data)
    closeConnection(conn)
    return redirect(url_for('index'))

@app.route('/hide', methods=['POST'])
def hide():
    data = request.get_json().get('selectedMedia', [])
    print(f"Hiding images: {data}")
    conn = connectDB(dbPath())
    toggleVisibility(conn, data, 1)
    closeConnection(conn)
    return redirect(url_for('index'))

@app.route('/info/<path:path>')
def info(path):
    return os.stat(path)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
