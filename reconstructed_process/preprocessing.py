import os, sys
import json
from dateutil import parser, tz
from sub_classification import *
import re
import pandas as pd
from sub_classification import *
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize



#"suburb": 'Melbourne', "pos": 1, "neg": 1, "neu": 1, 
# "compound": 1,"has_offensive": True/False,
# "offensive dict": {'shit':1,'fuck': 1}
filename = "./tweetsStream.json"
stopwords = stopwords.words("english")
stopwords = set(stopwords)

def read_list_sub(filename):
    #with open("./" + filename) as file:
    with open(filename) as file:
        subdata = json.load(file)
    return subdata

def read_sub(filename):
    with open("./" + filename) as file:
        subdata = json.load(file)
    return subdata
json_dict = read_sub(filename)

# find the language
def is_en_tweet(json_dict):
    if json_dict["lang"] == "en":
        return True

print(is_en_tweet(json_dict))

# find the hour time
def format_timestamp(json_dict):
    timestamp = json_dict["created_at"]
    time = parser.parse(timestamp)
    time = time.replace(tzinfo=tz.gettz("Australia/Melbourne"))
    hour = time.hour
    json_dict["hour"] = hour
    return json_dict

print(format_timestamp(json_dict)["hour"])

# find the suburb
def update_suburb(json_dict, suburb_dict):
    coordinates = json_dict["coordinates"] # json format
    if coordinates:
        suburb_name = locate(coordinates, suburb_dict)
        json_dict["suburb"] = suburb_name
    else:
        json_dict["suburb"] = None
    return json_dict
#print(get_suburb(json_dict, suburb_dict)["suburb"])

# whether contains offensive words && # contain which offesive words
def extract_context_free(input_df, class_type):
    input_df = input_df.set_axis(["Words", "Class"], axis=1, inplace=False)
    return input_df[input_df["Class"] == class_type]

def create_offensive_list(offensive_df):
    offensive_words = []
    offensive_df = extract_context_free(offensive_df, 1)
    for item in offensive_df["Words"]:
        if item == "0":
            continue
        words = item.split("/")
        for word in words:
            s = re.sub(u"\\(adj\\)|\\(v\\)", "", word)
            offensive_words.append(s)
    return list(set(offensive_words))

def contain_offensive(text, offensive_df):
    keyword = {}
    offensive_word_list = create_offensive_list(offensive_df)
    for offensive_word in offensive_word_list:
        if offensive_word in text:
            if offensive_word in keyword.keys():
                keyword[offensive_word] += 1
            else:
                keyword[offensive_word] = 1
    if len(keyword.keys()) > 0:
        return True, keyword
    else:
        return False, keyword

def preprocess_text(text, lemmatizer, stopwards, apply_stopword):
    free_url = re.sub(r'http\S+', '', text)
    plain_text = ''.join(item for item in free_url if (item.isalnum() or item == " "))
    
    words = word_tokenize(plain_text)
    output_list = []
    for w in words:
        lemmed_word = lemmatizer.lemmatize(w)
        if apply_stopword and (lemmed_word not in stopwards):
            output_list.append(lemmed_word)
        else:
            output_list.append(lemmed_word)
    return output_list, plain_text

def update_offensive(json_dict, offensive_df, stopwords, lemmatizer):
    wordlist, plaintext = preprocess_text(json_dict["text"], lemmatizer, stopwords, False)
    has_offensive, keywords = contain_offensive(plaintext, offensive_df)
    json_dict["has_offensive"] = has_offensive
    if has_offensive:
        json_dict["offensive_dic"] = keywords
    else:
        json_dict["offensive_dic"] = None
    return json_dict


# find the sentiment
def sentiment_analysis(json_dict, stopwords, lemmatizer):
    sid = SentimentIntensityAnalyzer()
    wordlist, plaintext = preprocess_text(json_dict["text"], lemmatizer, stopwords, True)
    json_dict["word_dict"] = wordlist
    sentiment_dict = sid.polarity_scores(plaintext)
    json_dict["sentiment_dict"] = sentiment_dict
    return json_dict

#print(sentiment_analysis(json_dict, stopwords, lemmatizer)["sentiment_dict"])   

def update_nonEng_tweet(json_dict):
    #json_dict["hour"] = hour
    #json_dict["suburb"]
    json_dict["has_offensive"] = None
    json_dict["offensive_dic"] = None
    json_dict["word_dict"] = None
    json_dict["sentiment_dict"] = None
    return json_dict

def update(json_dict):
    # load tweet input && suburb dict
    
    poly_filename = 'suburb_location.json'
    suburb_dict = read_polygon_data(poly_filename)

    #load offensive dic data
    offensive_data = pd.read_csv("MOL.csv")
    total_offensive = pd.DataFrame(offensive_data)
    offensive_df = total_offensive[["American English", "Class"]]

    # word analysis
    lemmatizer = WordNetLemmatizer()
    

    json_dict = format_timestamp(json_dict)

    json_dict = update_suburb(json_dict, suburb_dict)
    if is_en_tweet(json_dict):
        json_dict = update_offensive(json_dict, offensive_df, stopwords, lemmatizer)
        json_dict = sentiment_analysis(json_dict, stopwords, lemmatizer)
    else:
        json_dict = update_nonEng_tweet(json_dict)

    return json_dict

# read a single tweet
json_dict = read_sub(filename)
print(update(json_dict))

# read tweets within a list
path = "./real_data/"
files = os.listdir(path)

for file in files:
    print(file)
    filename = path + '/' + file
    json_dict = read_list_sub(filename)
    new_dict = update(json_dict)
    print(new_dict)
   
        
