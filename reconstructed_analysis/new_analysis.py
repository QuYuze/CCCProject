## Author: Juan Dai
## Student ID: 1025253
## Purpose: 
## 1. Do sentiment analysis for twitter data, group the useful
## words for each suburbs and their frequency
## 2. Do offensive language searching and group them by suburb and hours
## output the offensive words and frequecy

import pandas as pd
import math
import operator
########################## nighttime part  ##########################

def is_nighttime_tweet(hour, starttime, endtime):
    if hour >= starttime or hour <= endtime:
        return True
    else:
        return False


# update the sentiment_info for the corresponding tweet,
# with the sentiment_dict, suburb and 
# the summary dictioanry needed to be updated as input 
# output as updated dictionary
def update_sent_dict(sentiment_value, sub, sent_count_dic):
    if sub in sent_count_dic.keys():
        if sentiment_value > 0:
            if "pos" in sent_count_dic[sub].keys():
                sent_count_dic[sub]["pos"] += 1
            else:
                sent_count_dic[sub]["pos"] = 1
        elif sentiment_value == 0:
            if "neu" in sent_count_dic[sub].keys():
                sent_count_dic[sub]["neu"] += 1
            else:
                sent_count_dic[sub]["neu"] = 1
        else: 
            if "neg" in sent_count_dic[sub].keys():
                sent_count_dic[sub]["neg"] += 1
            else:
                sent_count_dic[sub]["neg"] = 1
    else:
        sent_count_dic[sub] = {}
        if sentiment_value > 0:
            sent_count_dic[sub]["pos"] = 1
        elif sentiment_value == 0:
            sent_count_dic[sub]["neu"] = 1
        else: 
            sent_count_dic[sub]["neg"] = 1
    return sent_count_dic

# compute the summary stats of score, 
# score = pos + 1 / neg + 1, 
# log_score = log (pos + 1/ neg + 1)
# total is the count of total tweets that has a non-neu sentiment
def comupute_summary_stats(sent_count_dic):
    scores = []
    log_scores = []
    totals = []
    for sub in sent_count_dic.keys():
        if "pos" not in sent_count_dic[sub].keys():
            sent_count_dic[sub]["pos"] = 0
        if "neg" not in sent_count_dic[sub].keys():
            sent_count_dic[sub]["neg"] = 0
        score = round((sent_count_dic[sub]["pos"] + 1)/(sent_count_dic[sub]["neg"] + 1), 4)
        log_score = round(math.log(score), 4)
        total = sent_count_dic[sub]["pos"] + sent_count_dic[sub]["neg"]

        totals.append(total)
        scores.append(score)
        log_scores.append(log_score)
    return scores, log_scores, totals



def output_nightcount_result(sent_count_dic, scores, log_scores, totals):
    new_df = pd.DataFrame(sent_count_dic.items(), columns=['Suburbs', 'Sentiment'])
    new_df['total'] = totals
    new_df["scores"] = scores
    new_df["log_scores"] = log_scores
    return new_df

def group_by_sub(input_df):
    sent_count_dic = {}
    #{"MEl":{"pos": 1, "neg":2}}
    for i in range(len(input_df)):
        sub = input_df.iloc[i]["suburb"] 
        sentiment_value = input_df.iloc[i]["compound"] 
        sent_count_dic = update_sent_dict(sentiment_value, sub, sent_count_dic)
    # score = pos + 1 / neg + 1, log_score = log (pos + 1/ neg + 1)
    scores, log_scores, totals = comupute_summary_stats(sent_count_dic)
    output_df = output_nightcount_result(sent_count_dic, scores, log_scores, totals)
    return output_df

output_name = "./nighttime_output_suburb.csv"
df = pd.read_csv(output_name)
#df = pd.DataFrame(data)
df_suburb_sentiment = group_by_sub(df)
df_suburb_sentiment.to_csv("./outputData/nighttime_suburb_groupping.csv", index= False)




# comput total positive number, total negative number, total tweets number(non-neutral)
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
        words_str = input_df.iloc[i]["useful_words"]
        # if words list is a str, then convert it using eval()
        words = eval(words_str)
        for word in words:
            if word in mydic.keys():
                mydic[word] += 1
            else:
                mydic[word] = 1
    output_dic = {}
    for k, v in mydic.items():
        if v > 10 and (not (k.isdigit())) and (len(k) > 3):
            output_dic[k] = v
    return dict(sorted(output_dic.items(), key=operator.itemgetter(1), reverse=True))

pos, neg = tweet_classification(df)
total_50 = list(word_count(df).items())[:50]
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


#########################  offensive part  #########################

def update_freq_count(index, offensive_words, off_freq_dic, index_count):
    # if words list is a str, then convert it using eval()
    offensive_words = eval(offensive_words)
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
    return off_freq_dic, index_count

def order_group_dic(off_freq_dic):
    for index in off_freq_dic.keys():
        off_freq_dic[index] = dict(sorted(off_freq_dic[index].items(), key=operator.itemgetter(1), reverse=True))
    return off_freq_dic



def output_count_off_result(off_freq_dic, index_count, index_name):
    new_df = pd.DataFrame(index_count.items(), columns=[index_name, 'count'])
    new_df["words"] = list(off_freq_dic.values())
    new_df.sort_values(index_name, inplace= True)
    new_df.to_csv("./outputData/offensive_" + index_name +"_groupping.csv", index= False)

def count_off_freq(input_df, index_name):
    off_freq_dic = {}
    index_count = {}
    for i in range(len(input_df)):
        #{hour:{"fuck":1}}
        index= input_df.iloc[i][index_name]
        offensive_words = input_df.iloc[i]["offensive_words"] 
        off_freq_dic, index_count = update_freq_count(index, offensive_words, off_freq_dic, index_count)
        
    off_freq_dic = order_group_dic(off_freq_dic)
    output_count_off_result(off_freq_dic, index_count, index_name)

    
    
df = pd.read_csv("offensive_df.csv")
#offensive group by hour
count_off_freq(df, "hour")

#offensive group by surburb
count_off_freq(df, "suburb")