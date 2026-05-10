import serial
import pymongo
import re
from datetime import datetime

# Σύνδεση με τη βάση MongoDB
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["wsn_project"]
collection = db["sensor_data"]

SERIAL_PORT = '/dev/ttyUSB0'
BAUD_RATE = 115200

try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    print("Συνδέθηκε επιτυχώς στο Mote! Αναμονή για δεδομένα...")
    print("Πάτα Ctrl+C για τερματισμό.\n")
except Exception as e:
    print("Δεν μπόρεσα να ανοίξω τη θύρα. Σφάλμα: {e}")
    exit()

try:
    while True:
        raw_data = ser.readline()
        # Μετατροπή σε κείμενο αγνοώντας τα binary σύμβολα του TinyOS
        line = raw_data.decode('utf-8', errors='ignore').strip()
        
        if line:
            
            print("Έλαβα: {line}")
            
            # Ψάχνουμε ΜΟΝΟ για το μοτίβο: ψηφία,κόμμα,ψηφία,κόμμα,ψηφία,κόμμα,ψηφία
            match = re.search(r'(\d+),(\d+),(\d+),(\d+)', line)
            
            if match:
                data = {
                    "Timestamp": datetime.now(),
                    "ID": int(match.group(1)),
                    "Count": int(match.group(2)),
                    "Temp": int(match.group(3)),
                    "Humidity": int(match.group(4))
                }
                collection.insert_one(data)
                print("---> [ΕΠΙΤΥΧΙΑ] Αποθηκεύτηκε στη βάση: {data}\n")

except KeyboardInterrupt:
    print("\nΟλοκληρώθηκε η καταγραφή.")
finally:
    if 'ser' in locals():
        ser.close()
