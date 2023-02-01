import sqlite3
import os 

import datetime
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
        print(row)
        
        # res[row[0]] = row
        res.append(row[1])
        
    conn.close()
    return res


def getArduinoMessages(curr_time):
    
    print('getting arduino messages since: ', curr_time)
    
    res = []
    
    conn = sqlite3.connect(ROOT_DIR+'db/sensors.db')
    
    query = "SELECT * FROM sendToArduino WHERE sent = ? AND timestamp <= ?;"
    params = (0, curr_time)
    
    cursor = conn.execute(query, params)
    results = cursor.fetchall()
    
    for row in results:
        res.append(row)
    conn.close()
    return res

def setArduinoMessageSent(id):
    
    conn = sqlite3.connect(ROOT_DIR+'db/sensors.db')
    
    stmt = "UPDATE sendToArduino SET sent=True WHERE id=?;"
    params = ( int(id), )
    
    conn.execute(stmt, params )
    conn.commit()
    conn.close()
    
    # return res
    
def addMessagetoSendArduino(message):
    
    conn = sqlite3.connect(ROOT_DIR+'db/sensors.db')
    
    stmt = "INSERT INTO sendToArduino (message) VALUES (?);"
    params = ( message, )
    
    conn.execute(stmt, params )
    conn.commit()
    conn.close()
    

if __name__ == '__main__':
    updateLED("HIGH")
    
    setArduinoMessageSent(2)
    
    getArduinoMessages(datetime.datetime.utcnow())
    print('above')
    # print(getLED())    