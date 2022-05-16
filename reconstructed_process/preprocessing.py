## Author: Juan Dai
## Student ID: 1025253
## purpose: preprocess twitter input and add necessary fields 
## into the original twitter for later analysis section

import os, sys
import json
from dateutil import parser, tz
from sub_classification import *
import re
import pandas as pd
from sub_classification import *
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk.corpus import stopwords
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
            s = s.strip()
            s = " " + s + " "
            offensive_words.append(s)
    return list(set(offensive_words))

def contain_offensive(text, offensive_df):
    keyword = {}
    offensive_words = []
    offensive_freq = []
    offensive_word_list = create_offensive_list(offensive_df)
    
    for offensive_word in offensive_word_list:
        text_ngrams = find_ngram(text, len(offensive_word))
        if offensive_word in text_ngrams:
            freq = text_ngrams.count(offensive_word)
            offensive_words.append(offensive_word)
            offensive_freq.append(freq)

    for i in range(len(offensive_words)):
        freq = offensive_freq[i]
        offensive_word = offensive_words[i]
        keyword[offensive_word] = freq

    if len(keyword.keys()) > 0:
        return True, keyword
    else:
        return False, keyword

def preprocess_text(text, stopwards, apply_stopword):
    free_url = re.sub(r'http\S+', '', text)
    free_url = free_url.replace(",", " ")
    plain_text = ''.join(item for item in free_url if (item.isalnum() or item == " "))
    plain_text = " " +plain_text + " "
    words = word_tokenize(plain_text)
    output_list = []
    for w in words:
        lemmed_word = w
        if apply_stopword and (lemmed_word not in stopwards):
            output_list.append(lemmed_word)
        else:
            output_list.append(lemmed_word)
    return output_list, plain_text

def update_offensive(json_dict, offensive_df, stopwords):
    wordlist, plaintext = preprocess_text(json_dict["text"], stopwords, False)
    has_offensive, keywords = contain_offensive(plaintext, offensive_df)
    json_dict["has_offensive"] = has_offensive
    if has_offensive:
        json_dict["offensive_dic"] = keywords
    else:
        json_dict["offensive_dic"] = None
    json_dict = format_off_dic(json_dict)
    return json_dict


# find the sentiment
def sentiment_analysis(json_dict, stopwords):
    sid = SentimentIntensityAnalyzer()
    wordlist, plaintext = preprocess_text(json_dict["text"], stopwords, True)
    json_dict["word_dict"] = wordlist
    sentiment_dict = sid.polarity_scores(plaintext)
    json_dict["sentiment_dict"] = sentiment_dict
    return json_dict

#print(sentiment_analysis(json_dict, stopwords, lemmatizer)["sentiment_dict"])   
def create_food_dic(food_df):
    food_dic = {}
    country_names = list(food_df.columns.values)
    for country in country_names:
        temp_food_list = []
        for cuisine in food_df[country]:
            cuisine = " " + cuisine + " "
            temp_food_list.append(cuisine)
        food_dic[country] = list(set(temp_food_list))
    return food_dic

def contain_food(plaintext, food_df):
    keyword = {}

    all_cusine = []
    all_country = []
    all_freq = []

    food_dict= create_food_dic(food_df)
    for country in food_dict.keys():
        for cuisine in food_dict[country]:
            text_ngrams = find_ngram(plaintext, len(cuisine))
            if cuisine in text_ngrams:
                freq = text_ngrams.count(cuisine)
                all_freq.append(freq)
                all_cusine.append(cuisine)
                all_country.append(country)

    for i in range(len(all_country)):
        country = all_country[i]
        cuisine = all_cusine[i]
        freq = all_freq[i]
        if country in keyword.keys():
            keyword[country][cuisine] = freq
        else:
            keyword[country] = {}
            keyword[country][cuisine] = freq    

    if len(keyword.keys()) > 0:
        return True, keyword
    else:
        return False, keyword


def update_food(json_dict, food_df, stopwords):
    wordlist, plaintext = preprocess_text(json_dict["text"],  stopwords, False)
    has_food, keywords = contain_food(plaintext, food_df)
    json_dict["has_food"] = has_food
    if has_food:
        json_dict["food_dic"] = keywords
    else:
        json_dict["food_dic"] = None
    json_dict = format_food_dic(json_dict)
    return json_dict
def find_ngram(text, n):
    ngrams = []
    length = len(text)
    if length >= n:
        for i in range(length - n + 1):
            temp_ngram = "".join(text[i : i+n])
            ngrams.append(temp_ngram)
    return ngrams
    

def format_food_dic(json_dict):
    food_dic = json_dict["food_dic"]
    if food_dic != None:
        for country in food_dic.keys():
            new_dic = {}
            for cuisine in food_dic[country].keys():
                new_dic[cuisine.strip()] = food_dic[country][cuisine]
            food_dic[country] = new_dic
        json_dict["food_dic"] = food_dic
    return json_dict

def format_off_dic(json_dict):
    off_dic = json_dict["offensive_dic"]
    if off_dic != None:
        new_dic = {}
        for offensive_word in off_dic.keys():
            new_dic[offensive_word.strip()] = off_dic[offensive_word]
        json_dict["offensive_dic"] = new_dic
    return json_dict
        

def update_nonEng_tweet(json_dict):
    #json_dict["hour"] = hour
    #json_dict["suburb"]
    json_dict["has_offensive"] = None
    json_dict["offensive_dic"] = None
    json_dict["has_food"] = None
    json_dict["food_dic"] = None
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

    #load food dic data
    food_data = pd.read_csv("food_key_words.csv")
    total_food = pd.DataFrame(food_data)
    food_df = total_food.drop(["Chinese", "Unnamed: 0"], axis= 1)
    

    json_dict = format_timestamp(json_dict)

    json_dict = update_suburb(json_dict, suburb_dict)
    if is_en_tweet(json_dict):
        json_dict = update_offensive(json_dict, offensive_df, stopwords)
        json_dict = update_food(json_dict, food_df, stopwords)
        json_dict = sentiment_analysis(json_dict, stopwords)
    else:
        json_dict = update_nonEng_tweet(json_dict)

    return json_dict

# read a single tweet
json_dict = read_sub(filename)
print(update(json_dict))


"""
# read tweets within a list
path = "./real_data/"
files = os.listdir(path)

for file in files:
    print(file)
    filename = path + '/' + file
    json_dict = read_list_sub(filename)
    new_dict = update(json_dict)
    print(new_dict)
   
"""   