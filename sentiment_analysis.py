import pandas as pd
import sys
import json
import re
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
from nltk.corpus import wordnet



# load data
data = pd.read_csv("output_tweet_with_time.csv")
all_df = pd.DataFrame(data)
all_df.reset_index(drop=True, inplace=False)
print("the start data length: " , len(all_df))

#print(all_df)
def filter_english(input_df):
    output_df = input_df.loc[input_df["lang"] == "en"]
    return output_df

df = filter_english(all_df)
print("the english data length: " , len(df))
#print(df)



lemmatizer = WordNetLemmatizer()


def find_target_tweet(synonyms, words):
    for syn in synonyms:
        if (syn in words):
            return True
    return False

def find_synonyms(keyword):
    synonyms = []

    for syn in wordnet.synsets(keyword):
        for i in syn.lemmas():
            if i.name() != "club":
                synonyms.append(i.name())
    out = list(set(synonyms))
    print(out)
    return out

#print(find_synonyms("nightclub"))



def preprocess_text(text, lemmatizer):
    #plain_txt = ' '.join(w for w in nltk.wordpunct_tokenize(text) if w.lower() in words)
    free_url = re.sub(r'http\S+', '', text)
    plain_text = ''.join(item for item in free_url if (item.isalnum() or item == " "))
    #plain_text = re.sub("[^a-zA-Z0-9]+", "", text)
    
    words = word_tokenize(plain_text)
    output_list = []
    for w in words:
        output_list.append(lemmatizer.lemmatize(w))
    return output_list, plain_text
        


def extract_related_data(input_df, keyword):
    mylist = []
    synonyms = find_synonyms(keyword)
    text_list = []
    text = []
    for i in range(len(input_df)):
        lemmed_words, plaintext = preprocess_text(input_df.iloc[i]['text'].lower(), lemmatizer)
        
        if find_target_tweet(synonyms, lemmed_words):
            #print(plaintext)
            text_list.append(lemmed_words)
            mylist.append(input_df.iloc[i])
            text.append(plaintext)
    temp_df = pd.DataFrame(mylist)
    new_df = pd.DataFrame()
    new_df["id"] = temp_df["id"]
    new_df["coordinates"] = temp_df["coordinates"]
    new_df["lang"] = temp_df["lang"]
    new_df["text"] = text
    #new_df["text_list"] = text_list
    new_df.reset_index(drop=True, inplace=True)
    return new_df

#related = extract_related_data(df, "nightclub")



def sentiment_analysis(input_df, keyword):
    sid = SentimentIntensityAnalyzer()
    df_character_sentiment = extract_related_data(input_df, keyword.lower())
    df_character_sentiment[['neg', 'neu', 'pos', 'compound']] = df_character_sentiment['text'].apply(sid.polarity_scores).apply(pd.Series)
    print(df_character_sentiment)
    
    return df_character_sentiment


keyword = sys.argv[1]
df_sentiment = sentiment_analysis(df, keyword)
df_sentiment.to_csv("sentiment_output.csv")


#python3 sentiment_analysis.py nightclub