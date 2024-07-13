
import os
import sqlite3
from typing import Dict, List, Generator, List
from utils import *
from yolov8 import detectClasses
from flask import Flask, render_template, send_file, request, redirect, url_for
from markupsafe import escape


def dbPath() -> str:
    """
    Database is created on the user's home directory.

    Returns:
        str: The path to the database file.
    """
    return os.path.join(os.path.expanduser("~"), ".pictopy.db")

def processImgs(conn: sqlite3.Connection, files: Generator[str, None, None]) -> None:
    """
    Processes images by extracting their hash values, detecting their classes, and storing them in the database.

    Args:
        conn: The database connection object.
        files: A generator of file paths.
    """
    
    objDetectionModel = pathOf("models/yolov8n.onnx")
    for file in files:
        imgHash = genHash(file)
        if hashExist(conn, imgHash):
            continue
        try:
            imgClass,_ = detectClasses(file, objDetectionModel)
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
                "imageID INTEGER PRIMARY KEY AUTOINCREMENT", 
                "hash TEXT UNIQUE", 
                "path TEXT", 
                "hidden INTEGER"
            ],
            "CLASS": [
                "classID INTEGER PRIMARY KEY AUTOINCREMENT", 
                "class TEXT UNIQUE"
            ],
            "JUNCTION": [
                "imageID INTEGER", 
                "classID INTEGER", 
                "FOREIGN KEY(imageID) REFERENCES MEDIA(imageID) ON DELETE CASCADE",
                "FOREIGN KEY(classID) REFERENCES CLASS(classID)",
                "PRIMARY KEY (imageID, classID)"
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

@app.route('/delete', methods=['POST'])
def delete():
    data = request.get_json().get('selectedImages', [])
    print(f"Deleting images: {data}")
    conn = connectDB(dbPath())
    deleteFromDB(conn, data)
    closeConnection(conn)
    return redirect(url_for('index'))

@app.route('/hide', methods=['POST'])
def hide():
    data = request.get_json().get('selectedImages', [])
    print(f"Hiding images: {data}")
    conn = connectDB(dbPath())
    toggleVisibility(conn, data, 1)
    closeConnection(conn)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
