@echo off
:: Navigate to the project directory
cd .\tbb-backend\

:: Check if the virtual environment folder exists
if not exist venv (
    echo Virtual environment not found, creating one...
    python -m venv venv
)

:: Activate the virtual environment
call venv\Scripts\activate

:: Install requirements
if exist requirements.txt (
    echo Installing dependencies from requirements.txt...
    pip install -r requirements.txt
) else (
    echo requirements.txt not found!
)

:: Run FastAPI application using uvicorn
echo Starting FastAPI application...
uvicorn run:app --host 0.0.0.0 --port 8000

:: Keep the window open to see any output
pause