data = '2025-04-05'
import sqlite3
conn = sqlite3.connect('trening.sqlite')
cur = conn.cursor()
cur.execute('''DELETE FROM Trening''')
conn.commit()
conn.close()