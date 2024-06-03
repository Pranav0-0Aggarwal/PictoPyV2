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

def executeQuery(conn: sqlite3.Connection, query: str) -> List[Tuple]:
    """Executes a query on the database.

    Args:
        conn: A sqlite3.Connection object.
        query: The SQL query to execute.

    Returns:
        A list of tuples containing the results of the query.
    """
    cursor = conn.cursor()
    cursor.execute(query)
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
    query = f"SELECT EXISTS(SELECT 1 FROM media WHERE hash='{hashValue}')"
    result = executeQuery(conn, query)
    return result[0][0] == 1
