take two terminals, one for backend and the other for frontend 

BACKEND
cd backend
python -m venv venv
venv\Scripts\activate  
pip install fastapi uvicorn
uvicorn main:app --reload

❗❗IMP NOTE: DO NOT CLOSE THE BACKEND TERMINAL

FRONTEND
cd frontend
npm install
npm run dev

click on : http://localhost:5173
