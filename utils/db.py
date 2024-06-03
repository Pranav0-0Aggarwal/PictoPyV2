import sqlite3
from typing import List, Tuple

def connectDB(dbPath: str) -> sqlite3.Connection:
    return sqlite3.connect(dbPath)

def createTable(conn: sqlite3.Connection, tableID: str, columns: List[str]) -> None:
    query = f"CREATE TABLE IF NOT EXISTS {tableID} ({', '.join(columns)})"
    executeQuery(conn, query)

def executeQuery(conn: sqlite3.Connection, query: str) -> List[Tuple]:
    cursor = conn.cursor()
    cursor.execute(query)
    return cursor.fetchall()

def closeConnection(conn: sqlite3.Connection) -> None:
    conn.commit()
    conn.close()

def hashExist(conn: sqlite3.Connection, hashValue: str) -> bool:
    query = f"SELECT EXISTS(SELECT 1 FROM media WHERE hash='{hashValue}')"
    result = executeQuery(conn, query)
    return result[0][0] == 1
