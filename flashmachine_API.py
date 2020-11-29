from typing import Optional, List
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from pydantic import BaseModel

from naverDictScraper import getDefinition


class Word_Request(BaseModel):
    word_array: List[str]



app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)




@app.get('/')
def read_root():
    print('You can do extra shit here, look')
    return {"hello": "world"}

@app.get('/single_word/{word}')
def get_single_word(word: str):
    result = getDefinition(word)
    return result


@app.get('/words/{joined_word}')
def get_multiple_words(joined_word:str):
    word_list = joined_word.split('_')
    result = []

    for w in word_list:
        result.append(getDefinition(w))

    return(result)

@app.post('/request_words/')
async def get_words_with_JSON(word_request: Word_Request):
    print('Confirm receipt of word request:')
    print(word_request)
    
    result = []
    for w in word_request.word_array:
        result.append(getDefinition(w))
    
    return result

