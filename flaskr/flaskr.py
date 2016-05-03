# all the imports
#import sqlite3
import sys
import ast
import json 
from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash, jsonify
from jinja2 import Environment, FileSystemLoader
import os

from Summary import *
import re, urllib2

##Chat Bot/BUZZFEED API IMPORTS
import requests
import random

# configuration
DATABASE = '/tmp/flaskr.db'
DEBUG = True
SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD = 'default'

# create our little application :)
app = Flask(__name__)
app.config.from_object(__name__)

#def connect_db():
    #return sqlite3.connect(app.config['DATABASE'])
status =  True

with open('data.txt', 'r') as myfile:
    lexiconDict = myfile.read().replace('\n', '')
lexiconDict = ast.literal_eval(lexiconDict)
#lexiconDict = json.dumps(lexiconDict)
#lexiconDict = json.loads(lexiconDict)
#print lexiconDict['happily']
@app.route('/')
def show_vanilla_home():
	return render_template('index.html', data = {'status': '', 'article_url': ''})

@app.route('/find/<param>')
def show_entries(param):
    #entries = [dict(title='hello', text='swaggy')]
	art = findArticle(str(param))
	return art
	
def summarize(title, content):

	st = SummaryTool()
	sentences_dic = st.get_sentences_ranks(content)
	summary = st.get_summary(title, content, sentences_dic)
	return jsonify(result=summary)

happy = ['cute', 'lol', 'yaaass', 'omg']
funny = ['lol', 'fail']
sad = ['fail']
#buzzfeed  = ['yaaass', 'omg', 'surprise', 'lol', 'cute', 'win', 'wtf', 'fail', 'ew', 'love', 'hate', 'amazing', 'blimey', 'splendid',  'trashy']

# anger = ['hate', 'fail']
# fear =  ['ew', 'creepy']
# anticipation =  ['omg', 'surprise', 'win', 'wtf', 'splendid']
# trust = ['win', 'splendid', 'love']
# surprise = ['blimey', 'amazing', 'omg', 'wtf']
# sadness = ['fail']
# joy = ['lol', 'amazing', 'splendid', 'cute', 'omg', 'yaaass', 'win']
# disgust = ['ew', 'trashy', 'fail']
# positive = ['yaass', 'lol', 'cute', 'win', 'love', 'splendid', 'amazing']
# negative = ['trashy', 'wtf', 'fail', 'hate', 'ew']

emotion_hash = {'anger': ['hate', 'fail'], 'fear': ['ew', 'creepy'], 'anticipation': ['omg', 'surprise', 'win', 'wtf', 'splendid'] ,'trust' : ['win', 'splendid', 'love'], 'surprise' : ['blimey', 'amazing', 'omg', 'wtf'], 'sadness' : ['fail'], 'joy' : ['lol', 'amazing', 'splendid', 'cute', 'omg', 'yaaass', 'win'], 'disgust' : ['ew', 'trashy', 'fail'], 'positive' : ['yaass', 'lol', 'cute', 'win', 'love', 'splendid', 'amazing'], 'negative' : ['trashy', 'wtf', 'fail', 'hate', 'ew']}
print emotion_hash
def getGif(param):
	adj = str(param)
	r = requests.get("http://api.giphy.com/v1/gifs/search?q="+adj+"&api_key=dc6zaTOxFJmzC")
	resp = r.json()
	return resp["data"][random.randint(0, len(resp["data"]) - 1)]["images"]["fixed_width"]["url"]
	
def findArticle(adj): #Provide string such as 'funny', 'happy', 'sad'
	if str(adj) in emotion_hash:
		adj = random.choice(emotion_hash[adj])
	else:
		ranK = random.choice(emotion_hash.keys())
		adj = random.choice(emotion_hash[ranK])
		
	buzzes = []
	for i in range(1,10):
		r = requests.get('http://www.buzzfeed.com/api/v2/feeds/'+str(adj)+'?p='+str(i))
		res = r.json()
		buzz = res['buzzes']
		for j in buzz:
			if j['language'] == 'en':
				buzzes.append(j)
			
	if buzzes:	#Generates summary
		num = random.randint(0, len(buzzes) - 1)
		url = "http://www.buzzfeed.com/api/v2/buzz/" + str(buzzes[num]['id'])
		r = requests.get(url) 
		resp = r.json()
		resp = resp['buzz']['sub_buzzes']
		content = ""
		for i in resp:
			content += i['description']
		title = buzzes[num]['title']
		title = urllib2.unquote(title)
		content = urllib2.unquote(content)
		st = SummaryTool()
		sentences_dic = st.get_sentences_ranks(content)
		summary = st.get_summary(title, content, sentences_dic)
			
		buzzURL = 'http://www.buzzfeed.com/' + buzzes[num]['username'] + "/" + buzzes[num]['uri']
		ret = {"summary": summary, "buzzURL": buzzURL, "gifURL": str(getGif(adj)), "title": title}
		return jsonify(ret)
		#"Summary: " + summary + "\n" + "Content Original: " + content + "Title: " + title
	return " "
	
if __name__ == '__main__':
    app.run(host=os.getenv('IP', '0.0.0.0'),port=int(os.getenv('PORT', 8080)))
