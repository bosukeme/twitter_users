from selenium import webdriver
from bs4 import BeautifulSoup
import requests
from pymongo import MongoClient
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException

from time import sleep
import re
import os
import pandas as pd
from twitter_scraper import Profile

import requests
import json


MONGO_URL="mongodb://Bloverse:uaQTRSp6d9czpcCg@64.227.12.212:27017/social_profiling?authSource=admin&readPreference=primary&appname=MongoDB%20Compass&ssl=false"
#mongo_url2="mongodb+srv://bloverse:b1XNYDtSQNEv5cAn@bloverse-production.fbt75.mongodb.net/inspirations?retryWrites=true&w=majority"

client= MongoClient(MONGO_URL, connect=False)
db = client.twitter_users



def load_entities():
    
    start=1
    end=2


    all_entities=[]
    for a in range(start, end):

        url="https://blovids-api-prod.herokuapp.com/v1/entities?page=" + str(a)+ "&per_page=30"
        #print(url)
        
        hello=requests.get(url)
        json_data = json.loads (hello.text)

        entities=[]
        for a in json_data['data']['articles']:
            b=a['entities']
            entities.append(b)
        all=[a for b in entities for a in b]
        entities=list(set(all))
        all_entities.append(entities)
    all_entities=[a for b in all_entities for a in b][:10]
    print("len: ", len(all_entities))
    return all_entities




def processed_entities():
    print("Starting.... hang in there")
    entities=load_entities()

    entity_df=pd.DataFrame()
    entity_df['entities']=entities
    
    
    processed_entities_collection=db.processed_entity_collection
    processed_entities= list(processed_entities_collection.find({}, {"_id":0, "entities":1}))
    processed_entities=list((val for dic in processed_entities for val in dic.values()))
    
    new_ent=[]
    for entity in entity_df['entities']:
        if entity not in processed_entities:
            processed_entities_collection.insert_one({'entities':entity}) 
            new_ent.append(entity)
            
    entities=list(processed_entities_collection.find({}, {"_id":0, "entities":1}))
    entities=list((val for dic in entities for val in dic.values()))


    print("new entities: ",len(new_ent))
    return new_ent





def get_users(new_ent):
    
    #entity=['obama','bbc-weather', 'lampard']
    driver=webdriver.Chrome(executable_path="C:\Program Files\chrome driver\chromedriver.exe")
    driver.wait = WebDriverWait(driver, 5)
    
    
    for ent in new_ent:
        try:
            url='https://twitter.com/search?q=' +ent+ '&src=typed_query&f=user'

            print(url)
            driver.get(url) ##open the site
            #driver.wait = WebDriverWait(driver, 10)
            sleep(5)



            class_path= "[class='css-901oao css-16my406 r-1qd0xha r-ad9z0x r-bcqeeo r-qvutc0']"
            driver.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, class_path)))
            main=driver.find_elements_by_css_selector(class_path)
            sleep(5)

            handle=[]
            for a in main:
                plain=a.text

                #if '@' in plain:
                if re.search('^\@', plain):
                    handle.append(plain.strip('@'))

            print(handle)


            #save_entity= [ent for a in range(len(handle))]


            df=get_meta_data(ent, handle)
            print(df)
            save_to_mongodb(df)
        except:
            pass

    #return 



    

def get_meta_data(ent, handle):
    if len(handle)==0:
        
        meta_data=[]
        for b in handle:
            try:
                profile = Profile(b)
                a=profile.to_dict()
                meta_data.append(a)

                df=pd.DataFrame(meta_data)
                df=df[df['followers_count']>5000]
                df=df[['name', 'username', 'followers_count']]
                df['entity']= [ent for c in range(len(df))]

            except:
                pass
            
    else:
        meta_data=[]
        for b in handle:
            try:
                profile = Profile(b)
                a=profile.to_dict()
                meta_data.append(a)

                df=pd.DataFrame(meta_data)
                df=df[df['followers_count']>5000]
                df=df[['name', 'username', 'followers_count']]
                df['entity']= [ent for c in range(len(df))]

            except:
                pass
        
    
    return df


def save_to_mongodb(df):
    
    
    # Load in the instagram_user collection from MongoDB
    twitter_user_collection = db.twitter_user_collection # similarly if 'testCollection' did not already exist, Mongo would create it
    
    cur = twitter_user_collection.find() ##check the number before adding
    print('We had %s instagram_user entries at the start' % cur.count())
    
     ##search for the entities in the processed colection and store it as a list
    twitter_user=list(twitter_user_collection.find({},{ "_id": 0, "username": 1})) 
    twitter_user=list((val for dic in twitter_user for val in dic.values()))


    #loop throup the handles, and add only new enteries
    for entity,name, username, followers_count in df[['entity', 'name','username', 'followers_count']].itertuples(index=False):
        if username  not in twitter_user:
            twitter_user_collection.insert_one({"entity": entity,"full_name":name, "username":username, "followers_count":followers_count}) ####save the df to the collection
    
    
  
    cur = twitter_user_collection.find() ##check the number after adding
    print('We have %s spacy entity entries at the end' % cur.count())
    



    
    
    
    
    
def call_all_func():
    
    new_ent=processed_entities()
    
    get_users(new_ent)
    
    
    print('we are done ')
    
    #return df
    
#call_all_func()
