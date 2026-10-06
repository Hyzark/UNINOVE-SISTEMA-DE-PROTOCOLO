import sqlite3

def create_connection():
    conn = sqlite3.connect("banco.db")
    return conn