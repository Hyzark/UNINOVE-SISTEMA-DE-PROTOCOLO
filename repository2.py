import sqlite3

connection = sqlite3.connect('banco.db')
connection.execute("PRAGMA foreign_keys = ON")
cursor = connection.cursor()


#deletar tabela historico
cursor.execute("DROP TABLE IF EXISTS historico")
connection.commit()


connection.close()