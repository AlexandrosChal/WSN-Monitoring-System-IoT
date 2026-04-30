# WSN-Monitoring-System-IoT
Implementation of an end-to-end Wireless Sensor Network (WSN) using IRIS and TelosB motes (TinyOS). Includes a star topology network, real-time data ingestion into MongoDB, a Grafana dashboard for visualization, and predictive analysis using Linear Regression and SARIMA models.

Ερώτημα 1: Προγραμματισμός και εγκατάσταση των motes
Στο παρόν ερώτημα υλοποιήθηκε ένα δίκτυο αισθητήρων σε τοπολογία αστέρα, με αυτόματη αρχικοποίηση και περιοδική αποστολή μετρήσεων από τους κόμβους-φύλλα στον κεντρικό κόμβο-πατέρα.  

1. Βασική Εγκατάσταση & Επιβεβαίωση (Blink)
Αρχικά επιβεβαιώθηκε η ορθή λειτουργία του TinyOS και των εργαλείων μεταγλώττισης χρησιμοποιώντας το παράδειγμα Blink.

Directory: ~/tinyos-main/apps/Blink

Εντολές:

Bash
sudo make clean
sudo make telosb install.1 bsl,/dev/ttyUSB0  # Για το 1ο mote
sudo make telosb install.2 bsl,/dev/ttyUSB1  # Για το 2ο mote

2. Υλοποίηση Τοπολογίας Αστέρα (Sensing)
Χρησιμοποιήθηκε ο κώδικας από το repository της εργασίας στον κατάλογο examples/Sensing.  

Αλλαγές στον Κώδικα
Α. Ρύθμιση Timer & Αποστολής (Κόμβοι-Φύλλα)

Αρχείο: Sampler/SensingPeriodicSamplerC.nc

Αλλαγή: Προσθήκη του interface Timer<TMilli> στα uses και ενεργοποίησή του στο startDone για αποστολή κάθε 20 δευτερόλεπτα (20000ms).  


// Στα uses:
interface Timer<TMilli> as Timer;

// Στο startDone:
if(e == SUCCESS) {
    call Timer.startPeriodic(20000); 
}

// Προσθήκη event:
event void Timer.fired() {
    if(sendBusy == FALSE) {
        sendBusy = TRUE;
        readNext();
    }
}


Αρχείο: Sampler/SensingPeriodicSamplerAppC.nc

Αλλαγή: Σύνδεση (wiring) του Timer component.


components new TimerMilliC() as Timer;
App.Timer -> Timer;


Β. Μορφοποίηση Εκτύπωσης (Κόμβος-Πατέρας)

Αρχείο: Base/SensingBaseC.nc

Αλλαγή: Τροποποίηση της συνάρτησης λήψης ώστε τα δεδομένα να τυπώνονται σε μία γραμμή.  


// Μέσα στο event RadioSampleMsgReceive.receive:
printf("%u,%lu,%u,%u\n", 
       call RadioAMPacket.source(msg), 
       recv_sample->sample_num, 
       recv_sample->temperature, 
       recv_sample->humidity);
printfflush();


3. Διαδικασία Μεταγλώττισης & Flash (Commands)
Βήμα 1: Προγραμματισμός Πατέρα (Base Station)

Directory: ~/tinyos-main/End-to-end-WSN-Project-2026/examples/Sensing/Base

Εντολές:

Bash
sudo make clean
sudo make telosb install.0 bsl,/dev/ttyUSB0
Βήμα 2: Προγραμματισμός Φύλλου (Leaf Node)

Directory: ~/tinyos-main/End-to-end-WSN-Project-2026/examples/Sensing/Sampler

Εντολές:

Bash
sudo make clean
sudo make telosb install.1 bsl,/dev/ttyUSB1


4. Μεταφορά σε Shared Folder
Στο make του Base και του Sampler
TINYOS_ROOT_DIR=/home/uses/tinyos-main

   

5. Επιβεβαίωση Λειτουργίας
Η επιτυχής ολοκλήρωση επιβεβαιώθηκε τρέχοντας την εντολή:

Bash
sudo java net.tinyos.tools.PrintfClient -comm serial@/dev/ttyUSB0:telosb
Τα δεδομένα εμφανίζονται πλέον στην οθόνη κάθε 20 δευτερόλεπτα στη μορφή: NodeID,SampleNum,Temp,Humidity.





## Ερώτημα 2: Αποθήκευση Δεδομένων σε Βάση Δεδομένων (MongoDB)

Ο στόχος αυτού του ερωτήματος είναι η αυτοματοποιημένη λήψη των μετρήσεων από τον Κόμβο-Πατέρα (μέσω της σειριακής θύρας USB) και η αποθήκευσή τους σε πραγματικό χρόνο σε μια βάση δεδομένων **MongoDB**.

### 1. Εγκατάσταση Απαιτούμενων Εργαλείων
Αρχικά, εγκαταστάθηκε η βάση δεδομένων MongoDB και οι απαραίτητες βιβλιοθήκες της Python στο σύστημα (Ubuntu):
```bash
# Εγκατάσταση και εκκίνηση της MongoDB
sudo apt update
sudo apt install -y mongodb
sudo systemctl start mongodb
sudo systemctl enable mongodb

# Εγκατάσταση βιβλιοθηκών Python (PyMongo και PySerial)
# Σημείωση: Χρησιμοποιείται η έκδοση <4.0 του pymongo για συμβατότητα με παλαιότερες εκδόσεις Python
pip3 install "pymongo<4.0" pyserial


2. Κατάλογος Εργασίας (Directory)
Όλα τα αρχεία (κώδικας TinyOS και Python scripts) βρίσκονται στον συνδεδεμένο κοινόχρηστο φάκελο (Shared Folder), ο οποίος είναι προσβάσιμος από το Ubuntu στο παρακάτω path:
~/tinyos-main/End-to-end-WSN-Project-2026/examples/Sensing

3. Εκτέλεση του Python Script (mongo_logger.py)
Το αρχείο mongo_logger.py είναι υπεύθυνο για την επικοινωνία με το Mote. Συνδέεται στη θύρα /dev/ttyUSB0, διαβάζει τα πακέτα, τα φιλτράρει χρησιμοποιώντας Regular Expressions (ώστε να απομονώσει τα ωφέλιμα δεδομένα από τα binary wrappers του TinyOS) και τα αποθηκεύει στη βάση.

Προσοχή: Πριν την εκτέλεση, το εργαλείο PrintfClient της Java πρέπει να είναι αυστηρά κλειστό για να μην μπλοκάρει τη σειριακή θύρα (sudo killall java).

Εκτέλεση καταγραφέα:

Bash
python3 ~/tinyos-main/End-to-end-WSN-Project-2026/examples/Sensing/mongo_logger.py
Το script αναμένει για δεδομένα και τυπώνει [ΕΠΙΤΥΧΙΑ] Αποθηκεύτηκε στη βάση: κάθε φορά που λαμβάνει επιτυχώς ένα νέο πακέτο (κάθε 20 δευτερόλεπτα).

4. Έλεγχος Αποθηκευμένων Δεδομένων (MongoDB Shell)
Για την επαλήθευση της σωστής καταγραφής των δεδομένων (Timestamp, ID, Count, Temp, Humidity), χρησιμοποιούμε το κέλυφος (shell) της MongoDB. Σε ένα νέο τερματικό εκτελούμε τα εξής:

Bash
# Είσοδος στο shell της MongoDB
mongo
Μέσα στο περιβάλλον της MongoDB, τρέχουμε τις παρακάτω εντολές:

JavaScript
// 1. Επιλογή της βάσης δεδομένων του project
use wsn_project

// 2. Εμφάνιση όλων των αποθηκευμένων μετρήσεων σε ευανάγνωστη μορφή
db.sensor_data.find().pretty()

// 3. Εμφάνιση μόνο των 5 πιο πρόσφατων μετρήσεων
db.sensor_data.find().sort({_id: -1}).limit(5).pretty()

// 4. Μέτρηση του συνολικού αριθμού αποθηκευμένων πακέτων
db.sensor_data.count()

// 5. Έξοδος από τη MongoDB
exit


## Ερώτημα 3: Οπτικοποίηση Δεδομένων (Real-Time Dashboard)

Για την οπτικοποίηση των δεδομένων σε πραγματικό χρόνο, επιλέχθηκε η υλοποίηση ενός ελαφριού και αυτόνομου **Web Application**, αντί για χρήση τρίτων εργαλείων όπως το Grafana. Η εφαρμογή αναπτύχθηκε με το framework **Flask (Python)** για το backend και τη βιβλιοθήκη **Chart.js (HTML/JavaScript)** για το frontend.

### 1. Εγκατάσταση Βιβλιοθηκών
Για τη δημιουργία του web server, εγκαταστάθηκε το framework Flask σε έκδοση συμβατή με το περιβάλλον της Python 3.5:
bash
pip3 install "MarkupSafe<2.0" "Flask<2.0"
2. Δομή Φακέλων (Directory Structure)
Ο κώδικας της εφαρμογής βρίσκεται στον φάκελο εργασίας του project (~/tinyos-main/End-to-end-WSN-Project-2026/examples/Sensing).:


3. Σχεδιαστικές Επιλογές (Dual Y-Axis)
Τα δεδομένα που λαμβάνονται από τους αισθητήρες (SHT11) του TelosB είναι ακατέργαστα ηλεκτρικά σήματα (Raw ADC values) και όχι μεταφρασμένες μονάδες (π.χ. Κελσίου ή %). Λόγω αυτού, η υγρασία κυμαίνεται σε τιμές ~7.000, ενώ η θερμοκρασία καταγράφεται ως 0.
Για να είναι το γράφημα ευανάγνωστο και να μην επικαλύπτονται οι γραμμές, υλοποιήθηκε Διπλός Άξονας Y (Dual Y-Axis) στο index.html. Η θερμοκρασία χρησιμοποιεί την αριστερή κλίμακα, ενώ η υγρασία τη δεξιά.

4. Οδηγίες Εκτέλεσης
Για την πλήρη λειτουργία του συστήματος απαιτείται η ταυτόχρονη εκτέλεση της καταγραφής (logger) και της προβολής (web server). Η διαδικασία γίνεται με χρήση δύο ξεχωριστών τερματικών:

Τερματικό 1: Καταγραφή Δεδομένων (Data Logger)

Bash
# Μεταφερόμαστε στον φάκελο εργασίας
cd ~/tinyos-main/End-to-end-WSN-Project-2026/examples/Sensing

# Εκτελούμε τον καταγραφέα
python3 mongo_logger.py
Τερματικό 2: Εκκίνηση Web Server

Bash
# Ανοίγουμε νέο τερματικό και μεταφερόμαστε στον ίδιο φάκελο
cd ~/tinyos-main/End-to-end-WSN-Project-2026/examples/Sensing

# Εκτελούμε το web app
python3 app.py
Προβολή του Dashboard:
Ανοίγουμε έναν Web Browser (π.χ. Firefox) στο Ubuntu και πληκτρολογούμε τη διεύθυνση:
http://localhost:5000

Το Dashboard εμφανίζεται και ανανεώνεται αυτόματα κάθε 5 δευτερόλεπτα, τραβώντας τις πιο πρόσφατες μετρήσεις από τη MongoDB.