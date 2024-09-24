from app.main import app
from app.Core.config import setting
if __name__ == "__main__":
    # app.run(debug=True)
    import uvicorn
    uvicorn.run("run:app", host=setting.HOST_NAME, port=setting.HOST_PORT, reload=True)

