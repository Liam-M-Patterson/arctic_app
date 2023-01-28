import sqlite3
import os 

# SOME ENV VARIABLES
from config import PI, ROOT_DIR

def updateLED(reading):
    
    state = 1 if reading == "HIGH" else 0
    print('db connect dir: ',ROOT_DIR+'db/sensors.db')
    conn = sqlite3.connect(ROOT_DIR+'db/sensors.db')
    conn.execute("INSERT INTO LED (state) VALUES (?);", (state, ))
    conn.commit()
    conn.close()

def getLED():
    
    # res = {}
    res = []
    conn = sqlite3.connect(ROOT_DIR+'db/sensors.db')
    cursor = conn.execute("SELECT * FROM LED;")
    for row in cursor:
        
        # res[row[0]] = row
        res.append(row[1])
        
    conn.close()
    return res


if __name__ == '__main__':
    updateLED("HIGH")
    
    print(getLED())