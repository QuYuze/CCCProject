import math

import pandas as pd
import sys
import re
import operator
from sub_classification import *
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize



# load data
data = pd.read_csv("output_tweet_with_time.csv")
all_df = pd.DataFrame(data)

all_df["timestamp"] = pd.to_datetime(all_df["timestamp"])
all_df["timestamp"] = all_df["timestamp"].apply(lambda x: x.strftime("%Y-%m-%d %H:%M:%S"))

print("the start data length: " , len(all_df))

#print(all_df)
def filter_english(input_df):
    output_df = input_df.loc[input_df["lang"] == "en"]
    return output_df

df = filter_english(all_df)
print("the english data length: " , len(df))
print(df["timestamp"])
#print(df.between_time("09:00", "10:00"))

def filter_by_time(start_time, end_time, df):
    
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors='ignore')

    df["hour"] = df["timestamp"].dt.hour
    output = df[(df["hour"] >= start_time) | (df["hour"] <= end_time)]
    return output

print(filter_by_time(23, 5, df))


lemmatizer = WordNetLemmatizer()
#en = spacy.load('en_core_web_sm')
#stopwords = en.Defaults.stop_words
stopwords = stopwords.words("english")
other_words = ["melbourne", "you", "a2c", "me", "thats", "dont", "australia", "today", "year", "much", "tonight", "even"]
for item in other_words:
    stopwords.append(item)
stopwords = set(stopwords)

def preprocess_text(text, lemmatizer, stopwards):
    #plain_txt = ' '.join(w for w in nltk.wordpunct_tokenize(text) if w.lower() in words)
    free_url = re.sub(r'http\S+', '', text)
    plain_text = ''.join(item for item in free_url if (item.isalnum() or item == " "))
    #plain_text = re.sub("[^a-zA-Z0-9]+", "", text)
    
    words = word_tokenize(plain_text)
    output_list = []
    for w in words:
        lemmed_word = lemmatizer.lemmatize(w)
        if lemmed_word not in stopwards:
            output_list.append(lemmed_word)
    return output_list, plain_text

def find_useful_words(input_df, stopwords):
    mylist = []
    text_list = []
    text = []
    for i in range(len(input_df)):
        lemmed_words, plaintext = preprocess_text(input_df.iloc[i]['text'].lower(), lemmatizer, stopwords)
        text_list.append(lemmed_words)
        mylist.append(input_df.iloc[i])
        text.append(plaintext)
    temp_df = pd.DataFrame(mylist)
    new_df = pd.DataFrame()
    new_df["id"] = temp_df["id"]
    new_df["coordinates"] = temp_df["coordinates"]
    new_df["lang"] = temp_df["lang"]
    new_df["text"] = text
    new_df["useful_words"] = text_list
    new_df.reset_index(drop=True, inplace=True)
    return new_df


def sentiment_analysis(input_df, stopwords, start_time, end_time):
    sid = SentimentIntensityAnalyzer()
    df_temp = filter_by_time(start_time, end_time, input_df)
    df_character_sentiment = find_useful_words(df_temp, stopwords)
    df_character_sentiment[['neg', 'neu', 'pos', 'compound']] = df_character_sentiment['text'].apply(sid.polarity_scores).apply(pd.Series)
    
    df_character_sentiment = df_character_sentiment[df_character_sentiment["compound"] != 0]
    print(df_character_sentiment)
    print(sum(df_character_sentiment["compound"]))
    return df_character_sentiment




start_time = sys.argv[1]
start_time = sys.argv[2]
df_sentiment = sentiment_analysis(df, stopwords, 23, 5)
df_sentiment.to_csv("sentiment_output_time.csv")


#python3 nighttime_sentiment.py 23 5
subfile = 'suburb_location.json'
filename = "sentiment_output_time.csv"
output_name = "./outputData/nighttime_output_suburb.csv"
suburb_classification(subfile, filename, output_name)

data = pd.read_csv(output_name)
df = pd.DataFrame(data)
def group_by_sub(input_df):
    mydic = {}
    #{"MEl":{"pos": 1, "neg":2}}
    for i in range(len(input_df)):
        sub = input_df.iloc[i]["suburb"] 
        sentiment_value = input_df.iloc[i]["compound"] 
        if sub in mydic.keys():
            if sentiment_value > 0:
                if "pos" in mydic[sub].keys():
                    mydic[sub]["pos"] += 1
                else:
                    mydic[sub]["pos"] = 1
            elif sentiment_value == 0:
                if "neu" in mydic[sub].keys():
                    mydic[sub]["neu"] += 1
                else:
                    mydic[sub]["neu"] = 1
            else: 
                if "neg" in mydic[sub].keys():
                    mydic[sub]["neg"] += 1
                else:
                    mydic[sub]["neg"] = 1
        else:
            mydic[sub] = {}
            if sentiment_value > 0:
                mydic[sub]["pos"] = 1
            elif sentiment_value == 0:
                mydic[sub]["neu"] = 1
            else: 
                mydic[sub]["neg"] = 1
    scores = []
    log_scores = []
    for sub in mydic.keys():
        if "pos" not in mydic[sub].keys():
            mydic[sub]["pos"] = 0
        if "neg" not in mydic[sub].keys():
            mydic[sub]["neg"] = 0
        score = round((mydic[sub]["pos"] + 1)/(mydic[sub]["neg"] + 1), 4)
        log_score = round(math.log(score), 4)
        scores.append(score)
        log_scores.append(log_score)
    new_df = pd.DataFrame(mydic.items(), columns=['Suburbs', 'Sentiment'])
    new_df["scores"] = scores
    new_df["log_scores"] = log_scores
    return new_df

df_suburb_sentiment = group_by_sub(df)
df_suburb_sentiment.to_csv("./outputData/nighttime_suburb_groupping.csv", index= False)


















###################### trial ###################### 

def tweet_classification(input_df):
    positive = input_df[input_df["compound"] > 0]
    negative = input_df[input_df["compound"] < 0]
    new_df = pd.DataFrame()
    new_df["pos"] = [len(positive)]
    new_df["neg"] = [len(negative)]
    new_df["total"] = [len(positive) + len(negative)]
    new_df.to_csv("./outputData/nighttime_tweet_count.csv", index =False)
    return positive, negative

def word_count(input_df):
    mydic = {}
    for i in range(len(input_df)):
        words = input_df.iloc[i]["useful_words"]

        for word in words:
            if word in mydic.keys():
                mydic[word] += 1
            else:
                mydic[word] = 1
    output_dic = {}
    for k, v in mydic.items():
        if v > 10 and (not (k.isdigit())) and (len(k) > 2
        ):
            output_dic[k] = v

    return dict(sorted(output_dic.items(), key=operator.itemgetter(1), reverse=True))

pos, neg = tweet_classification(df_sentiment)
total_50 = list(word_count(df_sentiment).items())[:50]
print(total_50)
print("*******pos: ********\n")
pos_50 = list(word_count(pos).items())[:50]
print(pos_50)

print("*******neg: ********\n")
neg_50 = list(word_count(neg).items())[:50]
print(neg_50)
nightword_count_df = pd.DataFrame()
nightword_count_df["total"] = total_50
nightword_count_df["pos"] = pos_50
nightword_count_df["neg"] = neg_50
nightword_count_df.to_csv("./outputData/nighttime_word_freq.csv", index = False)