# Check if DB file exists
# If it doesn't create it
# check if it contain all classes
# if not add them according to their indexs
# if conflit occurs delete DB and recreate

import sqlite3
from utils import createTable, executeQuery
from typing import List, Tuple

def createSchema(conn: sqlite3.Connection) -> None:
    """Creates tables for IMAGES, JUNCTION, and CLASS in the database.

    Args:
        conn: A sqlite3.Connection object.
    """
    createTable(conn, "IMAGES", [
        "imageID INTEGER PRIMARY KEY AUTOINCREMENT", 
        "hash TEXT UNIQUE", 
        "path TEXT", 
        "hidden INTEGER"
    ])
    createTable(conn, "CLASS", [
        "classID INTEGER PRIMARY KEY AUTOINCREMENT", 
        "class TEXT UNIQUE"
    ])
    createTable(conn, "JUNCTION", [
        "imageID INTEGER", 
        "classID INTEGER", 
        "FOREIGN KEY(imageID) REFERENCES IMAGES(imageID)", 
        "FOREIGN KEY(classID) REFERENCES CLASS(classID)",
        "PRIMARY KEY (imageID, classID)"
    ])


# NN
def classesExist(conn: sqlite3.Connection, classes: List[str]) -> bool:
    """Checks if all classes already exist in the CLASS table.

    Args:
        conn: A sqlite3.Connection object.
        classes: A list of class names to check.

    Returns:
        bool: True if all classes exist in the CLASS table, False otherwise.
    """
    result = executeQuery(conn, "SELECT class FROM CLASS ORDER BY classID")
    existing_classes = [row[0] for row in result]
    return existing_classes == classes

def groupByclasses(conn: sqlite3.Connection) -> List[Tuple[str, str]]:
    """Returns hashes grouped by classes from the database.

    Args:
        conn: A sqlite3.Connection object.

    Returns:
        list: A list of tuples where each tuple contains class name and concatenated hashes.
        list[0][0]: class name
        list[0][1]: concatenated paths
    """
    query = """
        SELECT c.class, GROUP_CONCAT(i.path)
        FROM CLASS c
        JOIN JUNCTION j ON c.classID = j.classID
        JOIN IMAGES i ON j.imageID = i.imageID
        GROUP BY c.class
    """
    return executeQuery(conn, query)
