import uvicorn

if __name__ == "__main__":
    uvicorn.run("app.main_post:app", host="0.0.0.0", port=8001, reload=True)
