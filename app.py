#!flask/bin/python
import requests
import json
from flask import Flask, jsonify, abort, request, make_response, session, send_from_directory
from flask_restful import Resource, Api
from flask_session import Session
app = Flask(__name__)

@app.route('/')
def index():
    return "Welcome to the index"
	
@app.route('/product/search')	
def productSearch():
	if 'name' in request.args:
		if not request.args['name']:
			return "Name can not be empty"
		try:
			
			# Attempt request for Best Buy
			req = 'https://api.bestbuy.com/v1/products(search=' + request.args['name'] + ')?format=json&show=sku,name,salePrice&apiKey=pfe9fpy68yg28hvvma49sc89'
			bb = requests.get(req)
			bbd = json.loads(bb.text)
			
			#Attempt request for Walmart
			req = 'http://api.walmartlabs.com/v1/search?apiKey=rm25tyum3p9jm9x9x7zxshfa&query=' + request.args['name']
			wm = requests.get(req)
			wmd = json.loads(wm.text)
			
			#If both lists are empty
			if wmd['totalResults'] == 0 and not bbd['products']:
				return "Both sites returned empty"
			#If Walmart list is empty	
			elif wmd['totalResults'] == 0:
				#Get lowest Best Buy price
				lowestB = search(bbd['products'])
				lowest = createJson(lowestB, 'BestBuy')
				return make_response(jsonify(lowest))
			#If BestBuy list is empty	
			elif not bbd['products']:
				#Get lowest Walmart price
				lowestW = search(wmd['items'])
				lowest = createJson(lowestW, 'Walmart')
				return make_response(jsonify(lowest))
			#if both lists are populated	
			else:
				#Get lowest Best Buy price
				lowestB = search(bbd['products'])
				#Get lowest Walmart price
				lowestW = search(wmd['items'])
				
				
				#Compare the two lowest prices
				if float(lowestW['salePrice']) < float(lowestB['salePrice']):
					lowest = createJson(lowestW, 'Walmart')
					return make_response(jsonify(lowest))
					
				else:
					lowest = createJson(lowestB, 'BestBuy')
					return make_response(jsonify(lowest))
				
			
		except:
			return "Something went wrong."
	else:
		return "Error 404, bad request\n  Try entering a value"

#Searches the given lists and returns the lowest object
def search(blist):
	price = 999999999.99
	obj = blist[0]
	for key in range (0, len(blist)):
		if int(blist[key]['salePrice']) < price:
			obj = blist[key]
			price = float(blist[key]['salePrice'])
			
	return obj

#Creates a Json of the data given to it	
def createJson(obj, store):
	#Initiate lowest json object
	lowest = {}
	
	lowest['location'] = store
	lowest['currency'] = 'CAD'
	lowest['bestPrice'] = obj['salePrice']
	lowest['productName'] = obj['name']
	
	return lowest
	
	
if __name__ == '__main__':
    app.run(debug=True)