from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import nest_asyncio
from pyngrok import ngrok
import uvicorn
from pydantic import BaseModel

class Details(BaseModel):
    f_name: str
    l_name: str

app = FastAPI()

#app.add_middleware(
#    CORSMiddleware,
#    allow_origins=['*'],
#    allow_credentials=True,
#    allow_methods=['*'],
#    allow_headers=['*'],
#)


@app.post('/forecast/')
def forecast(data: Details):
    return {'message': data}