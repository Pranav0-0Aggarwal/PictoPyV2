import sqlite3
from typing import List, Dict
from utils.fs import deleteFile, pathExist

def connectDB(dbPath: str) -> sqlite3.Connection:
    """Connects to the database at the given path.

    Args:
        dbPath: The path to the database file.

    Returns:
        A sqlite3.Connection object.
    """
    return sqlite3.connect(dbPath)

def createTable(conn: sqlite3.Connection, tableID: str, columns: List[str]) -> None:
    """Creates a table in the database with the given name and columns.

    Args:
        conn: A sqlite3.Connection object.
        tableID: The name of the table to create.
        columns: A list of column names.
    """
    query = f"CREATE TABLE IF NOT EXISTS {tableID} ({', '.join(columns)})"
    executeQuery(conn, query)

def createSchema(conn: sqlite3.Connection, tables: Dict[str, List[str]]) -> None:
    """Creates tables for MEDIA, JUNCTION, and CLASS in the database.

    Args:
        conn: A sqlite3.Connection object.
        tables: A dictionary where each key is a table name and each value is a list of column definitions.
    """
    for tableName, columns in tables.items():
        createTable(conn, tableName, columns)

def executeQuery(conn: sqlite3.Connection, query: str, params: List = (), rowID: int = 0) -> List[List]:
    """Executes a query on the database.

    Args:
        conn: A sqlite3.Connection object.
        query: The SQL query to execute.
        params: The parameters to be used in the query.
        rowID: An optional integer indicating whether to return the last row ID.

    Returns:
        A list of lists containing the results of the query, or the last row ID if rowID is 1.
    """
    cursor = conn.cursor()
    cursor.execute(query, params)
    if rowID == 1:
        return cursor.fetchall(), cursor.lastrowid
    return cursor.fetchall()

def closeConnection(conn: sqlite3.Connection) -> None:
    """Closes the connection to the database.

    Args:
        conn: A sqlite3.Connection object.
    """
    conn.commit()
    conn.close()

def hashExist(conn: sqlite3.Connection, hashValue: str) -> bool:
    """Checks if a hash value exists in the database.

    Args:
        conn: A sqlite3.Connection object.
        hashValue: The hash value to check.

    Returns:
        True if the hash value exists, False otherwise.
    """
    query = "SELECT EXISTS(SELECT 1 FROM MEDIA WHERE hash=?)"
    result = executeQuery(conn, query, [hashValue])
    return result[0][0] == 1

def groupByClass(conn: sqlite3.Connection, hidden: int = 0, groupOf: str = "path") -> Dict[str, List[str]]:
    """Returns paths grouped by classes from the database.

    Args:
        conn: A sqlite3.Connection object.
        hidden: Filter images by hidden status.
        groupOf: The column to be grouped.

    Returns:
        dict: A dictionary where each key is a class name and each value is a list of paths.
    """
    query = f"""
        SELECT c.class, GROUP_CONCAT(i.{groupOf})
        FROM CLASS c
        JOIN JUNCTION j ON c.classID = j.classID 
        JOIN MEDIA i ON j.mediaID = i.mediaID 
        WHERE i.hidden = ?
        GROUP BY c.class
    """
    result = {}
    for row in executeQuery(conn, query, [hidden]):
        result[row[0]] = row[1].split(',')
    return result

def toggleVisibility(conn: sqlite3.Connection, paths: List[str], hidden: int) -> None:
    """Switch visibility of images by changing value of hidden column.

    Args:
        conn: sqlite3.Connection object.
        paths: A list of paths to switch visibility.
        hidden: The new value of hidden column.
    """
    query = f"UPDATE MEDIA SET hidden=? WHERE path IN ({', '.join('?' * len(paths))})"
    executeQuery(conn, query, [hidden] + paths)

def listByClass(conn: sqlite3.Connection, classes: List[str], hidden: int = 0, groupOf: str = "path") -> List[str]:
    """Returns list of all paths associated with the given classes.

    Args:
        conn: sqlite3.Connection object.
        classes: A list of class names.
        hidden: Filter images by hidden status.
        groupOf: The column to be grouped.

    Returns:
        A list of paths.
    """
    result = []
    groups = groupByClass(conn, hidden, groupOf)
    for class_ in groups:
        if class_ in classes:
            result.extend(groups[class_])
    return result

def hideByClass(conn: sqlite3.Connection, classes: List[str]) -> None:
    """Hides images by class.

    Args:
        conn: sqlite3.Connection object.
        classes: A list of class names.
    """
    toggleVisibility(conn, listByClass(conn, classes, 0), 1)

def unhideByClass(conn: sqlite3.Connection, classes: List[str]) -> None:
    """Unhides images by class.

    Args:
        conn: sqlite3.Connection object.
        classes: A list of class names.
    """
    toggleVisibility(conn, listByClass(conn, classes, 1), 0)

def deleteFromDB(conn: sqlite3.Connection, paths: List[str]) -> None:
    """Deletes related rows from DB. Deletes files by path.

    Args:
        conn: sqlite3.Connection object.
        paths: A list of paths to delete.
    """
    query = f"DELETE FROM MEDIA WHERE path IN ({', '.join('?' * len(paths))})"
    executeQuery(conn, query, paths)
    deleteFile(paths)

def deleteByClass(conn: sqlite3.Connection, classes: List[str]) -> None:
    """Deletes images by class.

    Args:
        conn: sqlite3.Connection object.
        classes: A list of class names.
    """
    deleteFromDB(conn, listByClass(conn, classes))

# def cleanDB(conn: sqlite3.Connection) -> None:
#     """Filter unavailable paths from DB and delete them.
# 
#     Args:
#         conn: sqlite3.Connection object.
#     """
#     query = "SELECT path FROM MEDIA"
#     for path in executeQuery(conn, query):
#         if not pathExist(path[0]):
#             deleteFromDB(conn, path)

def cleanDB(conn: sqlite3.Connection) -> None:
    """Filter unavailable paths from DB and delete them.

    Args:
        conn: sqlite3.Connection object.
    """
    query = "SELECT path FROM MEDIA"
    paths = []
    for path in executeQuery(conn, query):
        if not pathExist(path[0]):
            paths.append(path[0])
    
    if paths:
        print(paths)
        deleteFromDB(conn, paths)

def insertIntoDB(conn: sqlite3.Connection, file: str, imgClass: List[str], imgHash: str) -> None:
    """Inserts image and its classes into the database.

    Args:
        conn: sqlite3.Connection object.
        file: The path to the image file.
        imgClass: A list of classes associated with the image.
        imgHash: The hash value of the image.
    """
    try:
        _, mediaID = executeQuery(conn, "INSERT INTO MEDIA(hash, path, hidden) VALUES(?, ?, 0)", [imgHash, file], 1)

        for className in imgClass:
            try:
                _, classID = executeQuery(conn, "INSERT INTO CLASS(class) VALUES(?)", [className], 1)
            except sqlite3.IntegrityError:
                classID = executeQuery(conn, "SELECT classID FROM CLASS WHERE class = ?", [className])[0][0]
            
            executeQuery(conn, "INSERT OR IGNORE INTO JUNCTION(mediaID, classID) VALUES(?, ?)", [mediaID, classID])

    except sqlite3.IntegrityError:
        executeQuery(conn, "UPDATE MEDIA SET path = ? WHERE hash = ?", [file, imgHash])
