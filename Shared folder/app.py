from flask import Flask, render_template, jsonify
import pymongo

app = Flask(__name__)

# Σύνδεση με MongoDB
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["wsn_project"]
collection = db["sensor_data"]

@app.route('/')
def index():
    
    return render_template('index.html')

@app.route('/api/data')
def get_data():
    # Παίρνει τις 30 πιο πρόσφατες μετρήσεις
    cursor = collection.find({}, {"_id": 0}).sort("Timestamp", -1).limit(30)
    data = list(cursor)
    
    # Αντιστροφή της λίστας για να εμφανίζονται χρονολογικά στο γράφημα
    data.reverse() 
    return jsonify(data)

if __name__ == '__main__':
    # Τρέχει τον server τοπικά στη θύρα 5000
    app.run(host='0.0.0.0', port=5000, debug=True)
