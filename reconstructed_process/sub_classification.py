## Author: Wentao Guo
## Student ID: 1256470
## Purpose: Identify the tweet post suburb by the coordinates data provided

# This is a sample Python script.
from shapely.geometry import multipolygon,point,polygon
import json
from collections import defaultdict
import numpy as np
import pandas as pd


# may subject to change when we build tweet filter when we can get data using twitter api
def point_construct(coor_in_str):
    #print(coor_in_str)
    if type(coor_in_str) == str:
        coor_in_str = coor_in_str.replace('\'','"')
        coor_in_dict = json.loads(coor_in_str)
    else:
        coor_in_dict = coor_in_str
    coor_in_point = point.Point(coor_in_dict['coordinates'])
    return coor_in_point

def read_polygon_data(filename):
    suburb_dict = defaultdict(None)
    with open(filename, 'r') as f:
        for f in f.readlines():
            value_json = json.loads(f)
            feature_list = value_json['features']
            for poly in feature_list:
                name = poly['properties']['name']
                poly_coordinates = poly['geometry']['coordinates']
                poly_list = []
                for small_poly in poly_coordinates[0]:
                    small_poly_obj = polygon.Polygon(small_poly)
                    poly_list.append(small_poly_obj)
                single_suburb = multipolygon.MultiPolygon(poly_list)
                suburb_dict[name] = single_suburb
    return suburb_dict


# the first parameter is coordinates in a string format, may change it when we use it as tweet filters,
# main reason is that we may get tweet information in json format
# suburb dict is constructed using read_polygon_data function
def locate(coor_in_str, suburb_dict):
    coor_in_point = point_construct(coor_in_str)
    for suburb_name, suburb_polygon in suburb_dict.items():
        if suburb_polygon.contains(coor_in_point) or suburb_polygon.touches(coor_in_point):
            return suburb_name
    return None

def change_whole_csv(df_filename, suburb_dict):
    file = pd.read_csv(df_filename)
    file['points'] = file['coordinates'].apply(lambda x: point_construct(x))
    # a = file.loc[0,'coordinates']
    # sb = point_construct(a)
    # print(1)
    file['suburb'] = file['coordinates'].apply(lambda x: locate(x, suburb_dict))
    return file


# Press the green button in the gutter to run the script.
def suburb_classification(subfile, filename, output_name):
    poly_filename = subfile #'suburb_location.json'
    suburb_dict = read_polygon_data(poly_filename)

    # locate one single tweet, one tweet should look similar to this
    tweet_info = {"id": "00ca3b55e4fb99c89662eb1bbb06f71c", "key": "00ca3b55e4fb99c89662eb1bbb06f71c",
                   "value": {"_id": "877069414851588096", "_rev": "1-0e63a906feb4f34acb21d812075f8950",
                             "created_at": "Tue Jun 20 07:43:38 +0000 2017", "id": 877069414851588100,
                             "id_str": "877069414851588096", "text": "Back on home turf for tonight's event... beer vs wine, the battle of the grain vs the grape\u2026 https://t.co/NbZTlsxcnQ",
                             "truncated": False, "entities": {"hashtags": [], "symbols": [], "user_mentions": [], "urls": [{"url": "https://t.co/NbZTlsxcnQ", "expanded_url": "https://www.instagram.com/p/BVja2aojNNH/", "display_url": "instagram.com/p/BVja2aojNNH/", "indices": [93, 116]}]},
                             "metadata": {"iso_language_code": "en", "result_type": "recent"}, "source": "<a href=\"http://instagram.com\" rel=\"nofollow\">Instagram</a>", "in_reply_to_status_id": None, "in_reply_to_status_id_str": None,
                             "in_reply_to_user_id": None, "in_reply_to_user_id_str": None, "in_reply_to_screen_name": None, "user": {"id": 18880928, "id_str": "18880928", "name": "Kirrily Waldhorn", "screen_name": "beer_diva", "location": "Australia", "description": "The girl who really knows her beer and beer gastronomy. Beer writer, educator and enthusiast! Editor of @beer__style : pairing beer to music & fashion", "url": "https://t.co/F5YOMu9yD5", "entities": {"url": {"urls": [{"url": "https://t.co/F5YOMu9yD5", "expanded_url": "http://www.beerdiva.com.au", "display_url": "beerdiva.com.au", "indices": [0, 23]}]}, "description": {"urls": []}}, "protected": False, "followers_count": 3703, "friends_count": 1914, "listed_count": 128, "created_at": "Sun Jan 11 21:45:12 +0000 2009", "favourites_count": 267, "utc_offset": 36000, "time_zone": "Sydney", "geo_enabled": True, "verified": False, "statuses_count": 2233, "lang": "en", "contributors_enabled": False, "is_translator": False, "is_translation_enabled": False, "profile_background_color": "EDECE9", "profile_background_image_url": "http://pbs.twimg.com/profile_background_images/30112337/twitterbg.jpg", "profile_background_image_url_https": "https://pbs.twimg.com/profile_background_images/30112337/twitterbg.jpg", "profile_background_tile": False, "profile_image_url": "http://pbs.twimg.com/profile_images/831944101826224128/usNzjRXX_normal.jpg", "profile_image_url_https": "https://pbs.twimg.com/profile_images/831944101826224128/usNzjRXX_normal.jpg", "profile_banner_url": "https://pbs.twimg.com/profile_banners/18880928/1406873112", "profile_link_color": "365E4F", "profile_sidebar_border_color": "D3D2CF", "profile_sidebar_fill_color": "EDECE9", "profile_text_color": "8AB7A9", "profile_use_background_image": True, "has_extended_profile": False, "default_profile": False, "default_profile_image": False, "following": False, "follow_request_sent": False, "notifications": False, "translator_type": "none"}, "geo": {"type": "Point", "coordinates": [-37.8064416, 144.9888888]}, "coordinates": {"type": "Point", "coordinates": [144.9888888, -37.8064416]}, "place": {"id": "01864a8a64df9dc4", "url": "https://api.twitter.com/1.1/geo/id/01864a8a64df9dc4.json", "place_type": "city", "name": "Melbourne", "full_name": "Melbourne, Victoria", "country_code": "AU", "country": "Australia", "contained_within": [], "bounding_box": {"type": "Polygon", "coordinates": [[[144.593741856, -38.433859306], [145.512528832, -38.433859306], [145.512528832, -37.5112737225], [144.593741856, -37.5112737225]]]}, "attributes": {}}, "contributors": None, "is_quote_status": False, "retweet_count": 0, "favorite_count": 0, "favorited": False, "retweeted": False, "possibly_sensitive": False, "lang": "en", "location": "melbourne"}}
    coordinates = tweet_info['value']['coordinates']
    suburb_name = locate(coordinates, suburb_dict)
    print(suburb_name)

    # change the whole csv file, shouldn't use anymore when we can filter
    df_filename = filename #'output_tweet_with_time.csv'
    df = change_whole_csv(df_filename, suburb_dict)
    df.to_csv(output_name, index= False)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
