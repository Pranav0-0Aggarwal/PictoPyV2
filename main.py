import os
import logging
from typing import Dict, List
from utils import *
from media import *
from flask import Flask, render_template, send_file, request, redirect, url_for, Response
from markupsafe import escape

def dataDir() -> str:
    """
    Data directory is created on the user's home directory.

    Returns:
        str: The path to the home directory.
    """
    directory = os.path.join(os.path.expanduser("~"), ".pictopy")
    os.makedirs(directory, exist_ok=True)
    return directory 

def dbPath() -> str:
    """
    Database is created on the user's home directory.

    Returns:
        str: The path to the database file.
    """
    return os.path.join(dataDir(), "database.db")

def logPath() -> str:
    """
    Log file is created on the user's home directory.

    Returns:
        str: The path to the log file.
    """
    return os.path.join(dataDir(), "log.txt")

def groupPaths(hidden, fileType, groupBy) -> str:
    """
    Classify files in the home directory and store the results in the database.

    Returns:
        JSON created from list of tuples where each tuple contains a directory name and a group of paths.
    """
    conn = connectDB(dbPath())
    createSchema(conn, 
        {
            "MEDIA": [
                "mediaID INTEGER PRIMARY KEY AUTOINCREMENT", 
                "hash TEXT UNIQUE", 
                "path TEXT UNIQUE",
                "directory TEXT",
                "fileType TEXT CHECK(fileType IN ('img', 'vid'))",
                "modifiedTime TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
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

    """
    Because of classifyMedia() the following that too much time for the initial render.
    classifyMedia(conn, pathOf("models/yolov8n.onnx"), populateMediaTable(conn, mediaPaths(homeDir())))
    """

    cleanDB(conn)

    if groupBy == "directory":
        populateMediaTable(conn, mediaPaths(homeDir()))
        result = groupByDir(conn, hidden, fileType)
    else:
        populateMediaTable(conn, mediaPaths(homeDir()))
        classifyMedia(conn, pathOf("models/yolov8n.onnx"), getUnlinkedMedia(conn))
        result = groupByClass(conn, hidden, fileType)

    closeConnection(conn)

    return jsonify(result)

app = Flask(__name__, template_folder=f"{pathOf('static')}")

# Configure logging
logging.basicConfig(filename=logPath(),
                    level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s %(name)s %(message)s')

@app.route('/')
def index():
    return redirect(url_for('groupMedia', fileType='img', groupBy='directory'))

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
    if fileType not in ["img", "vid"] or groupBy not in ["class", "directory"]:
        return redirect(url_for('index'))
    return groupPaths(0, fileType, groupBy)

@app.route('/hidden/<string:groupBy>')
def hidden(groupBy):
    if groupBy not in ["class", "directory"]:
        return redirect(url_for('index'))
    return groupPaths(1, "any", groupBy)

@app.route('/trash/<string:groupBy>')
def trash(groupBy):
    if groupBy not in ["class", "directory"]:
        return redirect(url_for('index'))
    return groupPaths(-1, "any", groupBy)

# Buttons

@app.route('/toTrash', methods=['POST'])
def toTrash():
    data = request.get_json().get('selectedMedia', [])
    print(f"Moving files to trash: {data}")
    conn = connectDB(dbPath())
    moveToTrash(conn, data)
    closeConnection(conn)
    return "reload"

@app.route('/delete', methods=['POST'])
def delete():
    data = request.get_json().get('selectedMedia', [])
    print(f"Deleting files: {data}")
    conn = connectDB(dbPath())
    deleteFromDB(conn, data)
    closeConnection(conn)
    return "reload"

@app.route('/hide', methods=['POST'])
def hide():
    data = request.get_json().get('selectedMedia', [])
    print(f"Hiding files: {data}")
    conn = connectDB(dbPath())
    toggleVisibility(conn, data, 1)
    closeConnection(conn)
    return "reload"

@app.route('/unhide', methods=['POST'])
def unhide():
    data = request.get_json().get('selectedMedia', [])
    print(f"Unhiding files: {data}")
    conn = connectDB(dbPath())
    toggleVisibility(conn, data, 0)
    closeConnection(conn)
    return "reload"

@app.route('/restore', methods=['POST'])
def restore():
    data = request.get_json().get('selectedMedia', [])
    print(f"Restoring files: {data}")
    conn = connectDB(dbPath())
    toggleVisibility(conn, data, 0)
    closeConnection(conn)
    return "reload"

@app.route('/logs')
def show_logs():
    try:
        with open(logPath(), 'r') as log_file:
            log_contents = log_file.read()
        return Response(log_contents, mimetype='text/plain')
    except FileNotFoundError:
        return "Log file not found.", 404

@app.route('/info/<path:path>')
def info(path):
    return os.stat(path)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
