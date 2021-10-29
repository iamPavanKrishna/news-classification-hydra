#! /usr/bin/python3                                                                                                      

from kafka import KafkaProducer                                                                                         
from random import randint                                                                                              
from time import sleep, time                                                                                                 
import sys
import pandas as pd

import os
from dotenv import load_dotenv
import requests
import json

# Sleep from Time library
from time import sleep
                                                                                                                        
BROKER = "broker:9092"                                                                                    
TOPIC = 'news-trainer'                                                                                                                                                                                 
                                                                                                                        
try:                                                                                                                    
    p = KafkaProducer(bootstrap_servers=BROKER)                                                                         
except Exception as e:                                                                                                  
    print(f"ERROR --> {e}")                                                                                             
    sys.exit(1)

load_dotenv()

url = "https://free-news.p.rapidapi.com/v1/search"

headers = {
    'x-rapidapi-host': "free-news.p.rapidapi.com",
    'x-rapidapi-key': os.getenv('API_KEY') # hide API key
    }

def news_streamer(topic,timeout):
    now = time()
    page_no = 1
    while (time() - now < 2 * timeout):
        querystring = {"q":topic,"lang":"en","page":str(page_no),"page_size":"25"}
        response = requests.request("GET", url, headers=headers, params=querystring)
        try:
            for article in response.json()['articles']:
                try:
                    message = article["topic"]+"//"+article["title"]+"//"+article["summary"]                                                                                       
                    print(f">>> {message.split('//')}")                                                                                           
                    p.send(TOPIC, bytes(message, encoding="utf8"))
                except:
                    print("message can't be sent")                                                                      
                sleep(1)
        except :
            print(f"max limit for topic {topic} reached")
        page_no += 1

if __name__ == "__main__":
    news_streamer(sys.argv[1],int(sys.argv[2]))