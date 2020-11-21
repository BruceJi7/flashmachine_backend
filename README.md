# flashmachine_backend
The back-end part for the flashmachine project: https://github.com/BruceJi7/flashmachine

Flashmachine is a project that turns a list of words into definitions that you can make into flashcards!

### About Flashmachine:

Flashmachine webscrapes word definitions from Naver Dict using BeautifulSoup4.
The definitions are extracted and stored in custom classes.
The definitions are formatted for use using a series of regex replacements.

FastAPI is used to provide the service as an API.
FastAPI accepts a string representing a list of words. The words are separated using underscores, to allow the user to search for multiple-word terms.
The API loops over the list and collects the results into a dictionary that is returned to the front end app.

### To use Flashmachine:
1. Download or clone the repository
2. Open a command prompt windown in the folder the repository is located in, or navigate there.
3. Install the python requirements:
```
pip install -r requirements.txt
```
4. Activate the environment:
```
.\flashmachine_env\scripts\activate.bat
```
5. Initialise the FastAPI server:
```
uvicorn flashmachine_API:app --reload
```
