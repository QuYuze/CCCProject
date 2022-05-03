import pandas as pd
import sys
import json
import nltk
import re
import operator
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk.stem import PorterStemmer
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
from nltk.corpus import wordnet
from datetime import datetime
from sub_classification import *



# load tweet data
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

def extract_hour(df):
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors='ignore')
    df["hour"] = df["timestamp"].dt.hour
    return df

df = extract_hour(df)



#load offensive dic data
offensive_data = pd.read_csv("MOL.csv")
total_offensive = pd.DataFrame(offensive_data)

offensive_df = total_offensive[["American English", "Class"]]
print(offensive_df)

def extract_context_free(input_df, class_type):
    input_df = input_df.set_axis(["Words", "Class"], axis=1, inplace=False)
    return input_df[input_df["Class"] == class_type]

offensive_df = extract_context_free(offensive_df, 1)
#print(extract_context_free(offensive_df, 1))

def create_offensive_list(input_df):
    offensive_words = []
    for item in input_df["Words"]:
        if item == "0":
            continue
        words = item.split("/")
        for word in words:
            s = re.sub(u"\\(adj\\)|\\(v\\)", "", word)
            offensive_words.append(s)

    return list(set(offensive_words))
print(create_offensive_list(offensive_df))
offensive_word_list = create_offensive_list(offensive_df)
print(len(offensive_word_list))

def contain_offensive(text, offensive_word_list):
    keyword = []
    for offensive_word in offensive_word_list:
        if offensive_word in text:
            keyword.append(offensive_word)
    if len(keyword) > 0:
        return True, keyword
    else:
        return False, keyword
        




def extract_related_data(input_df,offensive_word_list):
    mylist = []
    offensive_words = []

    for i in range(len(input_df)):
        is_contain, keywords = contain_offensive(input_df.iloc[i]["text"], offensive_word_list)
        if is_contain:
            #print(plaintext)
            offensive_words.append(keywords)
            mylist.append(input_df.iloc[i])
    temp_df = pd.DataFrame(mylist)
    new_df = pd.DataFrame()
    new_df["id"] = temp_df["id"]
    new_df["coordinates"] = temp_df["coordinates"]
    new_df["lang"] = temp_df["lang"]
    new_df["timestamp"] = temp_df["timestamp"]
    #new_df["text"] = temp_df["text"]
    new_df["hour"] = temp_df["hour"]
    new_df["offensive_words"] = offensive_words
    #new_df["text_list"] = text_list
    new_df.reset_index(drop=True, inplace=True)
    return new_df

df = extract_related_data(df,offensive_word_list)
print(df["coordinates"])
df.to_csv("offensive_tweet_collection.csv")

def recreate_off_list(input_str):
    text = input_str.replace('[','').replace(']','').replace("'",'')
    output_str = ''.join(item for item in text)
    if "," in output_str:
        output = output_str.split(",")
    else:
        output = [output_str]
    print(output)

recreate_off_list("[yes]")       

def count_off_freq(input_df, index_name):
    off_freq_dic = {}
    index_count = {}
    for i in range(len(input_df)):
        #{hour:{"fuck":1}}
        index= input_df.iloc[i][index_name]
        offensive_words = input_df.iloc[i]["offensive_words"] 
        if index in off_freq_dic.keys():
            index_count[index] += 1
            
            for word in offensive_words :
                if word in off_freq_dic[index].keys():
                    off_freq_dic[index][word] += 1
                else:
                    off_freq_dic[index][word]  = 1
        else:
            index_count[index] = 1
            off_freq_dic[index] = {}
            for word in offensive_words :
                if word in off_freq_dic[index].keys():
                    off_freq_dic[index][word] += 1
                else:
                    off_freq_dic[index][word]  = 1
        for index in off_freq_dic.keys():
            off_freq_dic[index] = dict(sorted(off_freq_dic[index].items(), key=operator.itemgetter(1), reverse=True))
        new_df = pd.DataFrame(index_count.items(), columns=[index_name, 'count'])
        new_df["words"] = list(off_freq_dic.values())
        new_df.sort_values(index_name, inplace= True)
        new_df.to_csv("./outputData/offensive_" + index_name +"_groupping.csv", index= False)
    

def output_grouping_csv(input_df, index_name):
    off_freq, index_count = count_off_freq(input_df, index_name)
    print("offensive word count: \n", off_freq)
    print("offensive hour count: \n", index_count)
    output_df = pd.DataFrame()
    output_df["hour"] = list(off_freq.keys())
    output_df["count"] = list(index_count.values())
    output_df["word_count"] = list(off_freq.values())
    output_df.to_csv("./outputData/offensive_" + index_name +"_groupping.csv", index= False)

count_off_freq(df, "hour")
#do the surburd classification, and then run the code above, can then obtain the offensive language count for each suburb
#and also the word_freq for that suburb under each hour


#python3 offensive.py


subfile = 'suburb_location.json'
filename = "offensive_tweet_collection.csv"
output_name = "./outputData/offensive_output_suburb.csv"
suburb_classification(subfile, filename, output_name)
data = pd.read_csv(output_name)
sub_df = pd.DataFrame(data)
df["suburb"] = sub_df["suburb"]
count_off_freq(df, "suburb")


