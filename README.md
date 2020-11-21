# flashmachine_backend
The back-end part for the flashmachine project

Flashmachine is a project that turns a list of words into definitions that you can make into flashcards!

### To use flashmachine:
1. Download or clone the repository
2. Install the python requirements:
```
pip install -r requirements.txt
```
3. Activate the environment:
```
.\flashmachine_env\scripts\activate.bat
```
4. Initialise the FastAPI server:
```
uvicorn flashmachine_API:app --reload
```
