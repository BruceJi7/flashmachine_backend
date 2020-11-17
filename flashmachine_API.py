from typing import Optional
from fastapi import FastAPI
from naverDictScraper import getDefinition


app = FastAPI()


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
    word_list = joined_word.split('%')
    result = []

    for w in word_list:
        result.append(getDefinition(w))

    return(result)