"""
This extracts used to get instragram users
"""
from flask import request
from flask_restful import Resource
import twitter_users
import pandas as pd
from ast import literal_eval
#from schema import DataSchema
import json

#data_schema = DataSchema()

class Twitter(Resource):   

    def post(self):
        #data=instagram_users.entities
        
       # result=instagram_users.call_all_func(data)
        result=twitter_users.call_all_func()

        #return {
         #   'Entity data': literal_eval(result)
        #}


