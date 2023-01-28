import sqlite3
import os 

ROOT_DIR = os.environ.get("ROOT_DIR")


def getWeather():
    
    res = {}
    conn = sqlite3.connect(ROOT_DIR+'db/sensors.db')
    cursor = conn.execute("SELECT * FROM weather;")
    for row in cursor:
        res[row[0]] = row
        
    conn.close()
    return res



if __name__ == '__main__':
    
    print(getWeather())