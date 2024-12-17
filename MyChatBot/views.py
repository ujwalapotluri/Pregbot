from django.shortcuts import render
from django.template import RequestContext
from django.contrib import messages
import pymysql
from django.http import HttpResponse
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from string import punctuation
from numpy import dot
from numpy.linalg import norm
from sklearn.feature_extraction.text import TfidfVectorizer
import re
import pandas as pd
import numpy as np

filename = []
word_vector = []

stop_words = set(stopwords.words('english'))
lemmatizer = WordNetLemmatizer()

def cleanPost(doc):
    tokens = doc.split()
    table = str.maketrans('', '', punctuation)
    tokens = [w.translate(table) for w in tokens]
    tokens = [word for word in tokens if word.isalpha()]
    tokens = [w for w in tokens if not w in stop_words]
    tokens = [word for word in tokens if len(word) > 1]
    tokens = [lemmatizer.lemmatize(token) for token in tokens]
    tokens = ' '.join(tokens)
    return tokens

def clean_str(string):
    string = re.sub(r"[^A-Za-z0-9(),!?\'\`]", " ", string)
    string = re.sub(r"\'s", " \'s", string)
    string = re.sub(r"\'ve", " \'ve", string)
    string = re.sub(r"n\'t", " n\'t", string)
    string = re.sub(r"\'re", " \'re", string)
    string = re.sub(r"\'d", " \'d", string)
    string = re.sub(r"\'ll", " \'ll", string)
    string = re.sub(r",", " , ", string)
    string = re.sub(r"!", " ! ", string)
    string = re.sub(r"\(", " \( ", string)
    string = re.sub(r"\)", " \) ", string)
    string = re.sub(r"\?", " \? ", string)
    string = re.sub(r"\s{2,}", " ", string)
    return cleanPost(string.strip().lower())

with open('dataset/question.json', "r") as f:
    lines=f.readlines()
    for line in lines:
        arr = line.split("#")
        cleanedLine = clean_str(arr[0])
        cleanedLine = cleanedLine.strip()
        cleanedLine = cleanedLine.lower()
        word_vector.append(cleanedLine)
        filename.append(arr[1])
    f.close()        

stopwords=stopwords = nltk.corpus.stopwords.words("english")
tfidf_vectorizer = TfidfVectorizer(stop_words=stopwords,use_idf=True, smooth_idf=False, norm=None, decode_error='replace')
tfidf = tfidf_vectorizer.fit_transform(word_vector).toarray()        
df = pd.DataFrame(tfidf, columns=tfidf_vectorizer.get_feature_names())
print(str(df))
print(df.shape)
df = df.values
X = df[:, 0:df.shape[1]]
X = np.asarray(X)
filename = np.asarray(filename)
word_vector = np.asarray(word_vector)


def MyChatBot(request):
    if request.method == 'GET':
       return render(request, 'index.html', {})

def User(request):
    if request.method == 'GET':
       return render(request, 'User.html', {})

def Logout(request):
    if request.method == 'GET':
       return render(request, 'index.html', {})

def test(request):
    if request.method == 'GET':
       return render(request, 'test.html', {})

def Register(request):
    if request.method == 'GET':
       return render(request, 'Register.html', {})

def ChatData(request):
    if request.method == 'GET':
        question = request.GET.get('mytext', False)
        cleanedLine = clean_str(question)
        cleanedLine = cleanedLine.strip()
        cleanedLine = cleanedLine.lower()
        testArray = []
        testArray.append(cleanedLine)
        testStory = tfidf_vectorizer.transform(testArray).toarray()
        similarity = 0
        user_story = 'Sorry! I am not trained for given question'
        print(testStory.shape)
        testStory = testStory[0]
        for i in range(len(X)):
            classify_user = dot(X[i], testStory)/(norm(X[i])*norm(testStory))
            if classify_user > similarity and classify_user > 0.50:
                similarity = classify_user
                user_story = filename[i]
        print(question+" "+user_story)
        return HttpResponse(user_story, content_type="text/plain")

def UserLogin(request):
    if request.method == 'POST':
      username = request.POST.get('username', False)
      password = request.POST.get('password', False)
      index = 0
      con = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = '', database = 'chatbot',charset='utf8')
      with con:    
          cur = con.cursor()
          cur.execute("select * FROM register")
          rows = cur.fetchall()
          for row in rows: 
             if row[0] == username and password == row[1]:
                index = 1
                break		
      if index == 1:
       context= {'data':'welcome '+username}
       return render(request, 'UserScreen.html', context)
      else:
       context= {'data':'login failed'}
       return render(request, 'User.html', context)

def Signup(request):
    if request.method == 'POST':
      username = request.POST.get('username', False)
      password = request.POST.get('password', False)
      contact = request.POST.get('contact', False)
      email = request.POST.get('email', False)
      address = request.POST.get('address', False)
      db_connection = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = '', database = 'chatbot',charset='utf8')
      db_cursor = db_connection.cursor()
      student_sql_query = "INSERT INTO register(username,password,contact,email,address) VALUES('"+username+"','"+password+"','"+contact+"','"+email+"','"+address+"')"
      db_cursor.execute(student_sql_query)
      db_connection.commit()
      print(db_cursor.rowcount, "Record Inserted")
      if db_cursor.rowcount == 1:
       context= {'data':'Signup Process Completed'}
       return render(request, 'Register.html', context)
      else:
       context= {'data':'Error in signup process'}
       return render(request, 'Register.html', context)
