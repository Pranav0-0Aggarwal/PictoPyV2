import sqlite3
from typing import List, Tuple

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

def executeQuery(conn: sqlite3.Connection, query: str, rowID: int = 0) -> List[Tuple]:
    """Executes a query on the database.

    Args:
        conn: A sqlite3.Connection object.
        query: The SQL query to execute.
        rowID: An optional integer indicating whether to return the last row ID.

    Returns:
        A list of tuples containing the results of the query, or the last row ID if rowID is 1.
    """
    cursor = conn.cursor()
    cursor.execute(query)
    if rowID == 1:
        return cursor.fetchall(), cursor.lastrowid
    return cursor.fetchall()
    # Prevent SQL injection (TBI)

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
    query = f"SELECT EXISTS(SELECT 1 FROM MEDIA WHERE hash='{hashValue}')"
    result = executeQuery(conn, query)
    return result[0][0] == 1


def groupByClass(conn: sqlite3.Connection, groupOf: str = "path") -> List[Tuple[str, str]]:
    """Returns paths grouped by classes from the database.

    Args:
        conn: A sqlite3.Connection object.
        groupOf: The column to be grouped.

    Returns:
        dict: A dictionary where each key is a class name and each value is a list of paths.
    """
    query = f"""
        SELECT c.class, GROUP_CONCAT(i.{groupOf})
        FROM CLASS c
        JOIN JUNCTION j ON c.classID = j.classID 
        JOIN MEDIA i ON j.imageID = i.imageID WHERE i.hidden = 0
        GROUP BY c.class
    """
    dict = {}
    for row in executeQuery(conn, query):
        dict[row[0]] = list(row[1].split(','))
    return dict

def toggleVisibility(conn: sqlite3.Connection, paths: List[str], hidden: int) -> None:
    """Switch visibility of images by changing value of hidden column.

    Args:
        conn: sqlite3.Connection object.
        paths: A list of paths to switch visibility.
        hidden: The new value of hidden column.
    """
    query = f"UPDATE MEDIA SET hidden={hidden} WHERE path IN ({', '.join(['?'] * len(paths))})"
    executeQuery(conn, query, paths)

def listByClass(conn: sqlite3.Connection, classes: List[str], groupOf: str = "path") -> List[str]:
    """Returns list of all paths associated with the given classes.
    (TBI) improve efficiency, as groupByClass() scans whole DB which is expensive.

    Args:
        conn: sqlite3.Connection object.
        classes: A list of class names.
        groupOf: The column to be grouped.

    Returns:
        A list of paths.
    """
    res = []
    groups = groupByClass(conn, groupOf)
    for group in groups:
        if group[0] in classes:
            paths.extend(group[1])
    return res

def hideByClass(conn: sqlite3.Connection, classes: List[str]) -> None:
    """Hides images by class.

    Args:
        conn: sqlite3.Connection object.
        classes: A list of class names.
    """
    toggleVisibility(conn, listByClass(conn, classes), 1)
    
def unhideByClass(conn: sqlite3.Connection, classes: List[str]) -> None:
    """Unhides images by class.

    Args:
        conn: sqlite3.Connection object.
        classes: A list of class names.
    """
    toggleVisibility(conn, listByClass(conn, classes), 0)

def delete(conn: sqlite3.Connection, paths: List[str]) -> None:
    """
    Delete images by path.
    Delete rows from MEDIA and JUNCTION tables using imageID. 

    Args:
        conn: sqlite3.Connection object.
        paths: A list of paths to delete.
    """

    

def deleteByClass(conn: sqlite3.Connection, classes: List[str]) -> None:
    """Deletes images by class.

    Args:
        conn: sqlite3.Connection object.
        classes: A list of class names.
    """