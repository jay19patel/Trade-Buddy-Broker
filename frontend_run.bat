
@echo off
:: ---- Frontend Setup ----
:: Navigate to the frontend directory
cd ..\tbb-frontend\

:: Install frontend dependencies
echo Installing frontend dependencies...
npm install

:: Run frontend in development mode
echo Starting frontend development server...
start npm run dev

:: Keep the window open to see output
pause