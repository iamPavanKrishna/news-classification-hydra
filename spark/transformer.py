#! /usr/bin/python3                                                                                                                                                                                                         
                                                                                                                        
from pyspark import SparkContext                                                                                        
from pyspark.sql import SparkSession                                                                                    
from pyspark.streaming import StreamingContext                                                                          
from pyspark.streaming.kafka import KafkaUtils               
import pickle
import pandas as pd
import numpy as np

# # MongoDB Setup
from pymongo import MongoClient
client = MongoClient()

client = MongoClient('mongo', 27017)

db = client['news_db']

articles = db['articles']

def handle_rdd(rdd):                                                                                                    
    if not rdd.isEmpty():                                                                                               
        global ss                                                                                                       
        df = ss.createDataFrame(rdd, schema=['TOPIC', 'TITLE', 'SUMMARY'])                                                
        df.show()
        df.write.saveAsTable(name='news_db.articles', format='mongo', mode='append')                                                                                                        
        # df.write.saveAsTable(name='default.nycparkingtickets', format='hive', mode='append')    
                           
# def predict_location(data):
#     model = pickle.load(open('XGBoost_model.pkl',"rb"))[0]
#     data = data.split()
#     X = pd.DataFrame([data])
#     prediction = model.predict(X)

#     return int(prediction[0])
                                                                                                                        
sc = SparkContext(appName="NEWSTRAINER")                                                                                     
ssc = StreamingContext(sc, 5)

ks = KafkaUtils.createDirectStream(ssc, ['news-trainer'], {'metadata.broker.list': 'broker:9092'})                       
                                                                                                                 
lines = ks.map(lambda x: x[1])

print(lines)
                                                                                                                 
# ss = SparkSession.builder.appName("NEWSTRAINER").config("spark.sql.warehouse.dir", "/user/hve/warehouse").config("hive.metastore.uris", "thrift://hadoop_hive:9083").enableHiveSupport().getOrCreate()

# ss = SparkSession.builder.appName("NEWSTRAINER").config("spark.mongodb.input.uri", "mongodb://mongo:27017/news-db.articles").config("spark.mongodb.output.uri", "mongodb://mongo:27017/news-db.articles").getOrCreate()                                                                                                                     

ss = SparkSession \
    .builder \
    .appName("NEWSTRAINER") \
    .config("spark.mongodb.input.uri", "mongodb://mongo/news_db.articles") \
    .config("spark.mongodb.output.uri", "mongodb://mongo/news_db.articles") \
    .getOrCreate()

ss.sparkContext.setLogLevel('WARN')            
                                                                                                            
# ks = KafkaUtils.createDirectStream(ssc, ['news-trainer'], {'metadata.broker.list': 'broker:9092'})                       
                                                                                                                 
# lines = ks.map(lambda x: x[1])

# print(lines)
                                                                                                            
transform = lines.map(lambda data: (data.split("//")[0], data.split("//")[1], data.split("//")[2]))

transform.foreachRDD(handle_rdd)                                                                                      
                                                                                                                        
ssc.start()                                                                                                             
ssc.awaitTermination()

# CREATE TABLE nycparkingtickets (text STRING, words INT, length INT, text STRING) ROW FORMAT DELIMITED FIELDS TERMINATED BY '\\|' STORED AS TEXTFILE;