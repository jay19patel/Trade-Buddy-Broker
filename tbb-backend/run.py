from app.main import app

if __name__ == "__main__":
    # app.run(debug=True)
    import uvicorn
    uvicorn.run("run:app", host="0.0.0.0", port=8000, reload=True)

