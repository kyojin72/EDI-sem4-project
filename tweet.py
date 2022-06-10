import requests
import os
import pandas as pd
import locationtagger as le
import time

class data_extract():

    def __init__(self):
        self.bearer_token = "AAAAAAAAAAAAAAAAAAAAAAOabQEAAAAAQDoJtk%2FE5Z%2Fp%2BxaMck%2FVofm1o04%3DIxZQW8LNNDU7FGWWYA6hi6anIq7FdLDbY9j7B0MbzwyeL9BuHU"

    def get_data(self,keyword):
        tweet_results = self.get_tweet(self.params(str(keyword+' -is%3Aretweet')))
        results = self.tweet_data(tweet_results)
        ret_vals = []
        for result in results:
            vals = []
            vals.append(result[0])
            vals.append(result[1])
            vals.append(result[2])
            if result[3] != '-1':
                vals.append(result[3])
            elif result[4] != '-1':
                vals.append(result[4])
            else:
                continue
            vals.append(str(result[5][:10]))
            ret_vals.append(tuple(vals))
        return ret_vals


    def params(self,query):
        return {'query': query +'&max_results=100'}

    def bearer_oauth(self,r):
        r.headers["Authorization"] = f"Bearer {self.bearer_token}"
        r.headers["User-Agent"] = "v2FilteredStreamPython"
        return r

    def get_tweet(self,query):
        response = requests.get(f"https://api.twitter.com/2/tweets/search/recent", auth=self.bearer_oauth, params=query)
        if response.status_code != 200:
            raise Exception("Cannot get stream (HTTP {}): {}".format(response.status_code, response.text))
        return response.json()

    def tweet_data(self,tweets):
        results = []
        tweet_ids= []
        for data in tweets['data']:
            tweet_ids.append(data['id'])
        for id in tweet_ids:
            info = []
            response = requests.get(f"https://api.twitter.com/2/tweets/{id}", auth=self.bearer_oauth, params={'expansions':'author_id','user.fields':'location','tweet.fields':'text','tweet.fields' : 'created_at'})
            if response.status_code != 200:
                time.sleep(900)
                continue
            result = response.json()
            info.append(id)
            if 'data' not in result:
                continue
            info.append(result['data']['text'])
            info.append(result['data']['author_id'])
            #print(result['includes'])
            #print(result['includes']['users'][0])
            locs = le.find_locations(text=result['data']['text'])
            if locs.other_countries :
                info.append(locs.other_countries[0])
            else:
                info.append('-1')
            if 'location' in result['includes']['users'][0]:
                locs = le.find_locations(text=result['includes']['users'][0]['location'])
                if locs.countries:
                    info.append(locs.countries[0])
                elif locs.other_countries:
                    info.append(locs.other_countries[0])
                else:
                    info.append('-1')
                #info.append(result['includes']['users'][0]['location'])
            else:
                info.append('-1')
            info.append(result['data']['created_at'])
            results.append(info)
        return results
            

if __name__ == "__main__":
    file_in = input("Enter the tag/name: ")
    corpus = file_in.split(',')
    data = pd.DataFrame()
    print(corpus)
    while(True):
        de = data_extract()
        for key_word in corpus:
            tweet_results = de.get_tweet(de.params(str(f'{key_word} OR #{key_word}')))
            results = de.tweet_data(tweet_results)
            data = data.append(results)
        print(data)