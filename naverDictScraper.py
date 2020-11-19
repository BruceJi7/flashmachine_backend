import codecs, re
import requests as req
from bs4 import BeautifulSoup
from pprint import pprint



headers = {'User-Agent' : 'Chrome/85.0.4183.12'}

korDictURL = r'https://endic.naver.com/search.nhn?sLn=en&searchOption=all&query='

SPACE_RX = re.compile(r'\s+')

DE_KOREAN_RX = re.compile(r'\([^A-Za-z]+\)')
DE_ENGLISH_RX = re.compile(r'[A-Za-z]+')
MATCH_KOREAN_RX = re.compile(r'[\uAC00-\uD7AF]+')

HANJA_RX = re.compile(r'[\u4e00-\u9fff]+')

NOUN_RX = re.compile(r'\[명사\]')
VERB_RX = re.compile(r'\[동사\]')
ADJECTIVE_RX = re.compile(r'\[형용사\]')
ADVERB_RX = re.compile(r'\[부사\]')



class WordIdiomWord():

    def __init__(self, searched_word, language, word_cell, definitions_cell):
        self.searched_word = searched_word
        self.word_cell = word_cell
        self.definitions_cell = definitions_cell
        self.language = language

   
    @property
    def result_type(self):
        return 'word_idiom'


    @property
    def result_word(self):
        return self.word_cell.find('a', class_=re.compile("N=a:wrd.entry")).text.capitalize()

    @property
    def hanja(self):
        if self.language == 'Korean': #If the searched word is Korean, remove Korean from the definition
            main_word = self.searched_word

            #Extract whole word span
            word_isolated = self.word_cell.find('span', class_="fnt_e30").text


            #Ditch the stupid extra space
            space_less = SPACE_RX.sub(' ', word_isolated).strip()

            hanja_present = HANJA_RX.search(space_less)

            if hanja_present:
                return hanja_present.group()
            else:
                return None
        else:
            return None

    @property
    def definition(self):
        meaning_span_element = self.definitions_cell.find('span', class_="fnt_k05")

        # Check BS4 found the element. Check the word exists.
        if meaning_span_element:
            meaning_span = meaning_span_element.text
        else:
            return None

        #Eliminate Korean brackets from definition
        if self.language == 'Korean':
            meaning_span = DE_KOREAN_RX.sub('', meaning_span).strip().capitalize()
        else:
            meaning_span = DE_ENGLISH_RX.sub('', meaning_span)

        #Replace Korean parts of speech with English ones:
        if '[' in meaning_span:
            meaning_span = NOUN_RX.sub('Noun:', meaning_span)
            meaning_span = VERB_RX.sub('Verb:', meaning_span)
            meaning_span = ADJECTIVE_RX.sub('Adj:', meaning_span)
            meaning_span = ADVERB_RX.sub('Adv:', meaning_span)

        meaning_span = SPACE_RX.sub(' ', meaning_span)

        return meaning_span

    @property
    def dictify(self):
        return {
            "language":self.language,
            "searched_term":self.searched_word,
            "result_type":self.result_type,
            "result_word":self.result_word,
            "hanja":self.hanja,
            "definition":self.definition
        }

class MeaningsWord():
    def __init__(self, searched_word, language, word_cell, definitions_cell):
        self.definitions_cell = definitions_cell
        self.word_cell = word_cell
        self.searched_word = searched_word
        self.result_word = searched_word.capitalize()     
        self.hanja = None
        self.language = language

    # @property
    # def language(self):
    #     english_present = bool(DE_ENGLISH_RX.search(self.searched_word))
    #     if english_present == True: #False, because the boolean is for what is REMAINING
    #         return 'English'
    #     else:
    #         return 'Korean'

    @property
    def result_type(self):
        return 'meaning'            
    
    @property
    def definition(self):

        main_word_element = self.word_cell.find('a', class_=re.compile("N=a:wrd.entry"))
        
        if main_word_element:
            main_word = main_word_element.text
        else:
            return None

        meaning_span = self.definitions_cell.find('span', class_="fnt_e07 _ttsText")
        if meaning_span:

            meaning_span = meaning_span.text

            if self.language == 'English':
                
                meaning_span = DE_ENGLISH_RX.sub('', meaning_span)
                meaning_span = SPACE_RX.sub(' ', meaning_span)

                return f'"{meaning_span}" 에서와 같이 {main_word}'
                
            else:

                
                meaning_span = DE_KOREAN_RX.sub('', meaning_span).strip().capitalize()
                meaning_span = SPACE_RX.sub(' ', meaning_span)
                
    
                if meaning_span:
                    return f'{main_word.capitalize()}, as in "{meaning_span}"'
                else:
                    return main_word.capitalize()

        else:
            return main_word.capitalize()

        
    @property
    def dictify(self):
        return {
            'language':self.language,
            'searched_term':self.searched_word,
            'result_type':self.result_type,
            'result_word':self.result_word,
            'hanja':self.hanja,
            'definition':self.definition
        }


def getDefinition(word):

    word_language = None
    korean_present = MATCH_KOREAN_RX.search(word)
    if korean_present:
        word_language = 'Korean'
    else:
        word_language = 'English'


    # Make Word Objects out of word-idiom section
    def word_idioms_to_objects(html_section, word_language):

        naver_word_results = html_section.find_all('dt')

        word_objects = []
        for w in naver_word_results:
            w_object = WordIdiomWord(word, word_language, w, w.find_next_sibling('dd'))
            w_dict_format = w_object.dictify

            word_objects.append(w_dict_format)
        
        return word_objects

    
    #Make Word Objects out of Meanings section
    def meanings_to_objects(html_section, word_language):
        word_titles = html_section.find_all('dt')
        word_objects = []

        for w in word_titles:
            w_object = MeaningsWord(word, word_language, w, w.find_next_sibling('dd'))
            w_dict_format = w_object.dictify

            word_objects.append(w_dict_format)

        return word_objects




    
    res = req.get(korDictURL + word, headers=headers)
    res.raise_for_status()

    soup = BeautifulSoup(res.text, features='html.parser')

    sections = soup.find_all('dl', class_='list_e2') # The page holds 2 'list_e2' sections, one for words, one for meanings :S

    word_idiom_section_word_objects = []
    meanings_section_word_objects = []

    if sections:
        #Sections[0] corresponds to 'words & idioms'
        word_idiom_section_word_objects = word_idioms_to_objects(sections[0], word_language)

    # If the word has a 'meanings' section - not all do
    if len(sections) > 1:
        #Sections[1] corresponds to 'meanings'
        meanings_section_word_objects =  meanings_to_objects(sections[1], word_language)

    combined_word_objects = word_idiom_section_word_objects + meanings_section_word_objects
    combined_word_objects_with_id = []
    for id_number, i in enumerate(combined_word_objects):

        updated_dict = i

        updated_dict['id'] = id_number

        combined_word_objects_with_id.append(updated_dict) 

    return { 
            'queryWord': word,
            'results' :combined_word_objects_with_id 
            }



def addJSONID(listOfDicts):

    result = []

    for id_number, i in enumerate(listOfDicts):

        updated_dict = i

        print(i)

        updated_dict['id'] = id_number

        result.append(updated_dict)
    
    return result


def load_words_from_file():

    fileloc = r"C:\Users\User\Desktop\reading_words.txt"

    with codecs.open(fileloc, 'r', 'utf-8') as f:
        words = f.readlines()
        words = [w.strip() for w in words]
    
    print(words)
    return words

word_results = getDefinition('화제')
# word_results = getDefinition('friend')

# loaded_words = load_words_from_file()

# word_results = [getDefinition(w) for w in loaded_words]
# pprint(word_results)
# word_results = addJSONID(word_results)
# print(word_results)
# for n in word_results:

#     for w in n:
#         print('----------------')
#         print(w)
