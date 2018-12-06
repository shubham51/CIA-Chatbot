import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet as wn
import re
import aiml
import subprocess
import os
import argparse
from MyKernel import MyKernel

DEBUG = True
SHOW_MATCHES = True

def course_code(sentence):
	try:
		words = re.compile('\w+').findall(sentence)
		new_sentence = ""
		for index, word in enumerate(words):
			if (word == "cs") and (index < len(words)-1) and (words[index+1].isdigit()):
				new_sentence = new_sentence + word
			else:
				new_sentence = new_sentence + word + " "
		return new_sentence
	except:
		return sentence

def remove_aiml_char(sentence):
    try:
        new_sentence = sentence.replace("_","")
        new_sentence = new_sentence.replace("*","")
        return new_sentence
    except:
        return sentence

dict = {'NN': 'NOUN', 'JJ': 'ADJ'}
dict['NNS'] = 'NOUN'
dict['NNP'] = 'NOUN'
dict['NNPS'] = 'NOUN'
dict['PRP'] = 'NOUN'
dict['PRP$'] = 'NOUN'
dict['RB'] = 'ADV'
dict['RBR'] = 'ADV'
dict['RBS'] = 'ADV'
dict['VB'] = 'VERB'
dict['VBD'] = 'VERB'
dict['VBG'] = 'VERB'
dict['VBN'] = 'VERB'
dict['VBP'] = 'VERB'
dict['VBZ'] = 'VERB'
dict['WRB'] = 'ADV'

grade_codes = ["o","a+","a","b+","b","c+","c","d+","d","f"]

BOT_INFO = {
    "name": "College Information Assistant (CIA)",
    "birthday": "Oct 15th 2018",
    "location": "DTU",
    "master": "DTU Administration",
    "website":"follow me on facebook",
    "gender": "Female",
    "age": "21",
    "size": "",
    "religion": "Humanity",
    "party": "All semester !"
}

k = MyKernel()
k.learn("aiml/standard/std-startup.xml")
k.respond("LOAD AIML B")

for key,val in BOT_INFO.items():
	k.setBotPredicate(key,val)

import pymysql
import base64
import getpass


connection = pymysql.connect(
    host='localhost',
    user='root',
    password='password',
    db='dtu_bot',
)

while(1):
    username = raw_input('\nUsername:\n')
    password = getpass.getpass()
    cursor = connection.cursor()
    try:
        sql = "SELECT * from users WHERE username = '%s'"%username
        cursor.execute(sql)
    except Exception as e:
        print("Exeception occured:{}".format(e))

    result = cursor.fetchone()
    if(str(result[1])!=base64.b64encode(str(password))):
        print("Wrong credentials. Please try again.\n")
        continue
    log = ""
    print("CIA:  Welcome\n")
    myinput = raw_input('CIA:  How can I help you?\nUser:  ')
    while(1):
        myinput = str(myinput)
        if(myinput == 'quit'):
            break
        if(myinput == 'logs'):
            try:
                sql = "SELECT conversation from logs WHERE username = '%s'"%username
                cursor.execute(sql)
            except Exception as e:
                print("Exeception occured:{}".format(e))
            if(cursor.fetchone() is None):
                print("CIA:  No logs to show!\n")
            else:
                print("---------------------------------------------------------------------")
                print(cursor.fetchone()[0])
                print("---------------------------------------------------------------------")
            myinput = raw_input('User:  ')
            continue
        log = log + "User:  " + myinput + "\n"
        sentence = myinput.lower()
        sentence = course_code(sentence)
        stop_words = set(stopwords.words('english'))
        word_tokens = word_tokenize(sentence)
        filtered_sentence = [w for w in word_tokens if not w in stop_words]
        temp = nltk.pos_tag(filtered_sentence)
        new_sentence = ""
        for i in temp:
            try:
                z = i[1]
                if (dict[z] != None):
                    part_speech = dict[z]
                else:
                    part_speech = 'NOUN'
                if(part_speech == 'NOUN'):
                    word = wn.morphy(i[0],wn.NOUN)
                elif(part_speech == 'VERB'):
                    word = wn.morphy(i[0],wn.VERB)
                elif(part_speech == 'ADV'):
                    word = wn.morphy(i[0],wn.ADV)
                elif(part_speech == 'ADJ'):
                    word = wn.morphy(i[0],wn.ADJ)
                word1 = wn.synsets(word)[0].lemmas()[0].name()
                if i[0] in grade_codes:
                    word1 = i[0]
            except:
                word1 = i[0]
            new_sentence = new_sentence+" "+word1.lower()
            new_sentence = remove_aiml_char(new_sentence)

        if DEBUG:
            matchedPattern = k.matchedPattern(myinput)
            response = k.respond(myinput)
            try:
                if SHOW_MATCHES:
                    print "Matched Pattern: "
                    print k.formatMatchedPattern(matchedPattern[0])
                    pattern = k.getPredicate("topic",'_global')
                    print "TOPIC:",pattern
                else:
                    print "-------------------------"
            except:
                print "No match found"
            print "Normal Response: ",response
            print "--------------------------------"
            print "new_sentence :",new_sentence
            matchedPattern = k.matchedPattern(new_sentence)
            response = k.respond(new_sentence)
            try:
                if SHOW_MATCHES:
                    print "Matched Pattern: "
                    print k.formatMatchedPattern(matchedPattern[0])
                    pattern = k.getPredicate("topic",'_global')
                    print "TOPIC:",pattern
                else:
                    print "-------------------------"
            except:
                print "No match found"
            print "New Response: ",response

        #--------------------------------------------------
        response = k.respond(myinput)
        response1 = k.respond(new_sentence)
        if response1 != "" and response1[0] == '$':
            response = response1[1:]
        print('\nCIA:  '+response+'\n')
        log = log + "CIA:  " + response + "\n"
        myinput = raw_input('User:  ')

    sql = "INSERT INTO logs (`conversation`, `username`)VALUES (%s, %s)"
    try:
        cursor = connection.cursor()
        cursor.execute(sql,(log, username))
    except Exception as e:
        print("Exeception occured:{}".format(e))
    connection.commit()
