import sqlite3


# Database setup
conn = sqlite3.connect("mydatabase.db")
cursor = conn.cursor()
cursor.execute("delete FROM timeslots WHERE id = 10;")
conn.commit()
conn.close()