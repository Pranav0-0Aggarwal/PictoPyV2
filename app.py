from config import *
from utils import *
from media import *
from typing import Dict, List
from flask import (
    Flask,
    render_template,
    send_file,
    request,
    redirect,
    url_for,
    Response,
    jsonify,
)

writing = False


def updateDB(groupBy: str = None) -> None:
    """
    Updates the database schema and populates the media table.
    Populates the media table with paths from the home directory.
    Optionally classifies media by class if specified.
    Cleans the database.

    Args:
        groupBy (str, optional): Specifies whether to classify media by 'class'. Defaults to None.
    """
    writeConn = connectDB(dbPath())
    createSchema(writeConn, dbSchema())

    populateMediaTable(writeConn, mediaPaths(homeDir()))
    if groupBy == "class":
        classifyMedia(
            writeConn,
            pathOf(yoloModelPath()),
            getUnlinkedMedia(connectDB(dbPath())),
        )
    cleanDB(writeConn)
    closeConnection(writeConn)


def groupPaths(hidden, fileType, groupBy) -> str:
    """
    Groups media paths by directory or class and returns them as JSON.

    Args:
        hidden (int): Specifies whether to include hidden files.
        fileType (str): Specifies the type of files to include ('img' or 'vid').
        groupBy (str): Specifies the grouping method ('directory' or 'class').

    Returns:
        str: JSON created from a list of tuples where each tuple contains a group name and a group of paths.
    """
    global writing
    if not writing:
        writing = True
        updateDB(groupBy)
        writing = False

    readConn = connectDB(dbPath())
    if groupBy == "directory":
        result = groupByDir(readConn, hidden, fileType)
    else:
        result = groupByClass(readConn, hidden, fileType)
    closeConnection(readConn)

    return jsonify(result)


def sendFile(filePath: str) -> Response:
    """
    Send a file specified by `filePath` to the client, after sanitizing it. 

    Args:
        filePath (str): The path to the file that should be sent to the client.

    Returns:
        File, or a custom error message with a 500 status code if an error occurs.
    """
    try:
        return send_file(decodeLinkPath(filePath))
    except Exception as e:
        app.logger.error(f"Error serving file: {e}")
        return "An error occurred while serving the file.", 500

app = Flask(__name__, template_folder=f"{pathOf('static')}")

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/static/<path:path>")
def staticFile(path):
    return sendFile(pathOf(path))



@app.route('/media/<path:path>')
def mediaFile(path):
    return sendFile(path)


@app.route("/thumbnail/<path:path>")
def thumbnail(path):
    return getThumbnail(decodeLinkPath(path))


# Sections


@app.route("/<string:fileType>/<string:groupBy>")
def groupMedia(fileType, groupBy):
    if fileType not in ["img", "vid"] or groupBy not in ["class", "directory"]:
        return redirect(url_for("index"))
    return groupPaths(0, fileType, groupBy)


@app.route("/hidden/<string:groupBy>")
def hidden(groupBy):
    if groupBy not in ["class", "directory"]:
        return redirect(url_for("index"))
    return groupPaths(1, "any", groupBy)


@app.route("/trash/<string:groupBy>")
def trash(groupBy):
    if groupBy not in ["class", "directory"]:
        return redirect(url_for("index"))
    return groupPaths(-1, "any", groupBy)


# Buttons


@app.route("/toTrash", methods=["POST"])
def toTrash():
    data = request.get_json().get("selectedMedia", [])
    print(f"Moving files to trash: {data}")
    conn = connectDB(dbPath())
    moveToTrash(conn, data)
    closeConnection(conn)
    return jsonify({"success": True})


@app.route("/delete", methods=["POST"])
def delete():
    data = request.get_json().get("selectedMedia", [])
    print(f"Deleting files: {data}")
    conn = connectDB(dbPath())
    deleteFromDB(conn, data)
    closeConnection(conn)
    return jsonify({"success": True})


@app.route("/hide", methods=["POST"])
def hide():
    data = request.get_json().get("selectedMedia", [])
    print(f"Hiding files: {data}")
    conn = connectDB(dbPath())
    toggleVisibility(conn, data, 1)
    closeConnection(conn)
    return jsonify({"success": True})


@app.route("/unhide", methods=["POST"])
def unhide():
    data = request.get_json().get("selectedMedia", [])
    print(f"Unhiding files: {data}")
    conn = connectDB(dbPath())
    toggleVisibility(conn, data, 0)
    closeConnection(conn)
    return jsonify({"success": True})


@app.route("/restore", methods=["POST"])
def restore():
    data = request.get_json().get("selectedMedia", [])
    print(f"Restoring files: {data}")
    conn = connectDB(dbPath())
    toggleVisibility(conn, data, 0)
    closeConnection(conn)
    return jsonify({"success": True})


@app.route("/info/<path:path>")
def info(path):
    conn = connectDB(dbPath())
    info = getInfoByPath(conn, decodeLinkPath(path))
    closeConnection(conn)
    return jsonify(info)


if __name__ == "__main__":

    app.run(debug=True, host="0.0.0.0")
    # On the off chance something occurs listner still stops after run is done
    print("Exiting Application, Listener stopped") 
