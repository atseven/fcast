from fastapi import FastAPI

@app.get('/forecast')
def forecast(name: str):
    return {'message': name}
