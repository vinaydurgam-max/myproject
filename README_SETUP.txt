Final Project - Local IoT Attack Detection (Arduino Integrated)
---------------------------------------------------------------

Contents:
- backend/         : Flask backend with SQLite and Arduino manager
- src/             : React frontend (Vite)
- arduino_sketch/  : Arduino sketch file IoT_Display_Controller.ino
- backend/database.db will be created on first run

Quick setup (Windows / Linux / Mac):

1) Backend
- Open terminal, create venv and activate
  python -m venv venv
  (Windows) venv\Scripts\activate
  (Linux/Mac) source venv/bin/activate
- Install backend deps:
  pip install -r backend/backend_requirements.txt
- Copy .env.example to backend/.env and set EMAIL configs if you want email alerts (or leave blank for testing)
- Start backend:
  python backend/app.py
  Backend serves API at http://localhost:5000/api/

2) Frontend
- In a new terminal (project root):
  npm install
  npm run dev
- Open http://localhost:5173

3) Arduino
- Open Arduino IDE, load arduino_sketch/IoT_Display_Controller.ino
- Install LiquidCrystal_I2C library if using I2C LCD
- Connect Arduino via USB to the machine running the backend
- Backend automatically scans serial ports and will send CONNECTED message when it finds the Arduino

Notes:
- To test without Arduino, the backend will continue to run and frontend will work normally.
- Detection is triggered by clicking "Detect Attack" on the frontend; backend will send ATTACK message to Arduino and log in SQLite.