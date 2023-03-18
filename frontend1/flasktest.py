from flask import Flask, render_template, url_for,request
import string
import re
import pandas as pd
import emoji
import demoji
import nltk
nltk.download('punkt')
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize
from sinling import SinhalaTokenizer as tokenizer,SinhalaStemmer as stemmer, POSTagger,preprocess, word_joiner,word_splitter
import os

import pygtrie as trie

from sinling.config import RESOURCE_PATH
from sinling.core import Stemmer
import pickle
from sklearn.preprocessing import LabelEncoder # to convert classes to number
import joblib 

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('homecopy.html')


@app.route('/about')
def about_page():
    return render_template('aboutus.html')

@app.route('/contact')
def contact_page():
    return render_template('contactus.html')


@app.route('/signup')
def signup_page():
    return render_template('signup.html')

@app.route('/login')
def login_page():
    return render_template('loginpage.html')

@app.route('/premium')
def premium_page():
    return render_template('premium.html')


@app.route('/', methods=['POST'])
def predict():
    text = request.form['Text']

    text = re.sub("[a-zA-Z]", " ", text) # remove english letters
    text = re.sub('\n', ' ', text) # remove \n from text
    text = re.sub(r'\d+', '', text) #remove number
    text = re.sub(r'#|@\w*', ' ',text) #remove @ mentions
    text = re.sub(r'http\S+', '', text) # remove links
    text = re.sub(' +', ' ',text) # remove extra space
    text = text.strip() #remove whitespaces

    joy = ['\U0001F600', '\U0001F602', '\U0001F603', '\U0001F604',
          '\U0001F606', '\U0001F607', '\U0001F609', '\U0001F60A',
          '\U0001F60B', '\U0001F60C', '\U0001F60D', '\U0001F60E',
          '\U0001F60F', '\U0001F31E', '\U0000263A', '\U0001F618',
          '\U0001F61C', '\U0001F61D', '\U0001F61B', '\U0001F63A',
          '\U0001F638', '\U0001F639', '\U0001F63B', '\U0001F63C',
          '\U00002764', '\U0001F496', '\U0001F495', '\U0001F601',
          '\U00002665','\U00002764']#joy

    anger = ['\U0001F62C', '\U0001F620', '\U0001F610',
            '\U0001F611', '\U0001F620', '\U0001F621', '\U0001F616',
            '\U0001F624', '\U0001F63E']#anger
    disgust= ['\U0001F4A9']#disgust
    fear = ['\U0001F605', '\U0001F626', '\U0001F627', '\U0001F631',
            '\U0001F628', '\U0001F630', '\U0001F640']#fear
    sad = ['\U0001F614', '\U0001F615', '\U00002639', '\U0001F62B',
            '\U0001F629', '\U0001F622', '\U0001F625', '\U0001F62A',
            '\U0001F613', '\U0001F62D', '\U0001F63F', '\U0001F494']#sad
    surp = ['\U0001F633', '\U0001F62F', '\U0001F635', '\U0001F632']#surprise

    emojilist = {'joy':joy, 'anger':anger, 'disgust':disgust, 'fear':fear, 'sad':sad, 'surprise':surp}

    def remove_punctuation(text):
        if isinstance(text, str):
            return text.translate(str.maketrans('', '', string.punctuation))
        else:
            return text
    text = remove_punctuation(text)
    
    # def remove_emojis(text):
    #     new_text = []
    #     for char in text:
    #         if char not in emoji.UNICODE_EMOJI['en']:
    #             new_text.append(char)
    #     return ''.join(new_text)
    # text1 = remove_emojis(text)

    def extract_emojis(text):
        emoji = ' '.join(c for c in text if c in emoji.UNICODE_EMOJI['en'])
        return emoji
    
    emoji = extract_emojis(text)

    allemoji = joy + anger + disgust + fear + sad + surp
    def concern_emojis(text):
        return ' '.join(c for c in text if c in allemoji)
    
    con_emoji = concern_emojis(emoji)

    demoji.download_codes()
    def get_emoji_meaning(e):
        return demoji.replace_with_desc(e)
    
    con_emoji_text = get_emoji_meaning(con_emoji)
    con_emoji_text = remove_punctuation(con_emoji_text)

    stemmer = PorterStemmer()

    # Tokenize the sentence into words
    words = word_tokenize(con_emoji_text)

    # Create a list to store the stemmed words
    stemmed_words = []

    # Loop through each word in the sentence and stem it
    for word in words:
        stemmed_word = stemmer.stem(word)
        stemmed_words.append(stemmed_word)

    # Convert the list of stemmed words back into a sentence
    stemmed_sentence = ' '.join(stemmed_words)

    # english-sinhala dictionary
    dictionary = {}
    os.chdir('frontend1\cleaned.csv')
    df= pd.read_csv("./emojiSinhala.csv")
    dictionary_file = df["En,sinhala"]

    for line in dictionary_file:
        key, value = line.strip().split(",")
        dictionary[key] = value

    def translate_english(x):
        for word1 in x.split():
            new_word = ''.join(i for i in word1 if not i.isdigit())
            x = x.replace(word1, new_word)
        for word in x.split():
            word2 = "".join(l for l in word if l not in string.punctuation)
            if re.match('[a-zA-Z]', word2) is not None:
                word1 = word2.lower()
                translated_word = dictionary.get(word1)
                if translated_word is None:
                    translated_word = ''
                x = x.replace(word, translated_word)
        return x
    con_emoji_text_sinhala = translate_english(con_emoji_text)

    stopwords_set = ["සහ","සමග","සමඟ","අහා","ආහ්","ආ","ඕහෝ","අනේ","අඳෝ","අපොයි","පෝ","අයියෝ","ආයි","ඌයි","චී","චිහ්","චික්","හෝ‍","දෝ",
                 "දෝහෝ","මෙන්","සේ","වැනි","බඳු","වන්","අයුරු","අයුරින්","ලෙස","වැඩි","ශ්‍රී","හා","ය","නිසා","නිසාවෙන්","බවට","බව","බවෙන්","නම්","වැඩි","සිට",
                 "දී","මහා","මහ","පමණ","පමණින්","පමන","වන","විට","විටින්","මේ","මෙලෙස","මෙයින්","ඇති","ලෙස","සිදු","වශයෙන්","යන","සඳහා","මගින්","හෝ‍",
                 "ඉතා","ඒ","එම","ද","අතර","විසින්","සමග","පිළිබඳව","පිළිබඳ","තුළ","බව","වැනි","මහ","මෙම","මෙහි","මේ","වෙත","වෙතින්","වෙතට","වෙනුවෙන්",
                 "වෙනුවට","වෙන","ගැන","නෑ","අනුව","නව","පිළිබඳ","විශේෂ","දැනට","එහෙන්","මෙහෙන්","එහේ","මෙහේ","ම","තවත්","තව","සහ","දක්වා","ට","ගේ",
                 "එ","ක","ක්","බවත්","බවද","මත","ඇතුලු","ඇතුළු","මෙසේ","වඩා","වඩාත්ම","නිති","නිතිත්","නිතොර","නිතර","ඉක්බිති","දැන්","යලි","පුන","ඉතින්",
                 "සිට","සිටන්","පටන්","තෙක්","දක්වා","සා","තාක්","තුවක්","පවා","ද","හෝ‍","වත්","විනා","හැර","මිස","මුත්","කිම","කිම්","ඇයි","මන්ද","හෙවත්",
                 "නොහොත්","පතා","පාසා","ගානෙ","තව","ඉතා","බොහෝ","වහා","සෙද","සැනින්","හනික","එම්බා","එම්බල","බොල","නම්","වනාහි","කලී","ඉඳුරා",
                 "අන්න","ඔන්න","මෙන්න","උදෙසා","පිණිස","සඳහා","රබයා","නිසා","එනිසා","එබැවින්","බැවින්","හෙයින්","සේක්","සේක","ගැන","අනුව","පරිදි","විට",
                 "තෙක්","මෙතෙක්","මේතාක්","තුරු","තුරා","තුරාවට","තුලින්","නමුත්","එනමුත්","වස්",'මෙන්',"ලෙස","පරිදි","එහෙත්"]
    
    def remove_stopwords_SINHALA(text):
        wordlist = []
        for w in text.split(' '):
            if w not in stopwords_set:
                wordlist.append(w)
        return ' '.join(wordlist)
    
    text1 = remove_stopwords_SINHALA(text1)


    __all__ = [
        'SinhalaStemmer'
    ]


    def _load_stem_dictionary():
        stem_dict = dict()
        with open(os.path.join(RESOURCE_PATH, 'stem_dictionary.txt'), 'r', encoding='utf-8') as fp:
            for line in fp.read().split('\n'):
                try:
                    base, suffix = line.strip().split('\t')
                    stem_dict[f'{base}{suffix}'] = (base, suffix)
                except ValueError as _:
                    pass
        return stem_dict


    def _load_suffixes():
        suffixes = trie.Trie()
        with open(os.path.join(RESOURCE_PATH, 'suffixes_list.txt'), 'r', encoding='utf-8') as fp:
            for suffix in fp.read().split('\n'):
                suffixes[suffix[::-1]] = suffix
        return suffixes


    class SinhalaStemmer(Stemmer):
        def __init__(self):
            super().__init__()
            self.stem_dictionary = _load_stem_dictionary()
            self.suffixes = _load_suffixes()

        def stem(self, word):
            if word in self.stem_dictionary:
                return self.stem_dictionary[word]
            else:
                suffix = self.suffixes.longest_prefix(word[::-1]).key
                if suffix is not None:
                    return word[0:-len(suffix)], word[len(word) - len(suffix):]
                else:
                    return word, ''
    stemmer = stemmer()
    def stem_word(word: str) -> str:
        word= translate_to_sinhala(word)
        """
        Stemming words
        :param word: word
        :return: stemmed word
        """
        if len(word) < 4:
            return word

        # remove 'ට'
        if word[-1] == 'ට':
            return word[:-1]

        # remove 'ම'
        if word[-1] == 'ම':
            return word[:-1]

        # remove 'ද'
        if word[-1] == 'ද':
            return word[:-1]

        # remove 'ටත්'
        if word[-3:] == 'ටත්':
            return word[:-3]

        # remove 'එක්'
        if word[-3:] == 'ෙක්':
            return word[:-3]

        # remove 'යේ'
        if word[-2:] == 'යේ':
            return word[:-2]

        # remove 'ගෙ' (instead of ගේ because this step comes after simplifying text)
        if word[-2:] == 'ගෙ':
            return word[:-2]

        # remove 'එ'
        if word[-1:] == 'ෙ':
            return word[:-1]

        # remove 'ක්'
        if word[-2:] == 'ක්':
            return word[:-2]

        # remove 'වත්'
        if word[-3:] == 'වත්':
            return word[:-3]

        word=stemmer.stem(word)
        word=word[0]

        # else
        return word
    text1 = stem_word(text1)
    full_text = text1 + con_emoji_text_sinhala 

    A=[]
    A.append(full_text)
    DF = pd.read_csv('cleaned.csv')
    count_vector = pickle.load(open('BOW.pkl',"rb"))
    test_vector = count_vector.transform(A).toarray()

    encoder = LabelEncoder()

    y = encoder.fit_transform(DF['Class'])
    classifier = joblib.load('random_forest')

    text_predict_class = encoder.inverse_transform(classifier.predict(test_vector))
    output = text_predict_class[0]
    # print(A[0], 'is: ',text_predict_class[0])
    # Perform sentiment analysis on the text
    return render_template('homecopy.html' ,prediction_text=output) # replace sentiment_result with your actual result




if __name__ == "__main__":
    app.run(debug=True)












#
# from flask import Flask,render_template,request,url_for,session,redirect,flash
# from flask_mysqldb import MySQL
#
# app=Flask(__name__)
#
# app.config["MYSQL_HOST"]="localhost"
# app.config["MYSQL_USER"]="root"
# app.config["MYSQL_PASSWORD"]=""
# app.config["MYSQL_DB"]="register"
# app.config["MYSQL_CURSORCLASS"]="DictCursor"
# mysql=MySQL(app)
#
# @app.route("/",methods=['GET','POST'])
# def index():
#     if 'alogin' in request.form:
#         if request.method == 'POST':
#             aname = request.form["aname"]
#             apass = request.form["apass"]
#             try:
#                 cur = mysql.connection.cursor()
#                 cur.execute("select * from admin where aname=%s and apass=%s", [aname, apass])
#                 res = cur.fetchone()
#                 if res:
#                     session["aname"] = res["aname"]
#                     session["aid"] = res["aid"]
#                     return redirect(url_for('admin_home'))
#                 else:
#                     return render_template("index.html")
#             except Exception as e:
#                 print(e)
#             finally:
#                 mysql.connection.commit()
#                 cur.close()
#     elif 'register' in request.form:
#         if request.method == 'POST':
#             uname = request.form["uname"]
#             password = request.form["upass"]
#             age = request.form["age"]
#             address = request.form["address"]
#             contact = request.form["contact"]
#             mail = request.form["mail"]
#             cur = mysql.connection.cursor()
#             cur.execute('insert into users (name,password,age,address,contact,mail) values (%s,%s,%s,%s,%s,%s)',
#                         [uname, password, age, address, contact, mail])
#             mysql.connection.commit()
#         return render_template("index.html")
#
#     elif 'ulogin' in request.form:
#         if request.method == 'POST':
#             name = request.form["uname"]
#             password = request.form["upass"]
#             try:
#                 cur = mysql.connection.cursor()
#                 cur.execute("select * from users where name=%s and password=%s", [name, password])
#                 res = cur.fetchone()
#                 if res:
#                     session["name"] = res["name"]
#                     session["pid"] = res["pid"]
#                     return redirect(url_for('user_home'))
#                 else:
#                     return render_template("index.html")
#             except Exception as e:
#                 print(e)
#             finally:
#                 mysql.connection.commit()
#                 cur.close()
#     return render_template("index.html")
#
# @app.route("/user_profile")
# def user_profile():
#     cur = mysql.connection.cursor()
#     id=session["pid"]
#     qry = "select * from users where pid=%s"
#     cur.execute(qry,[id])
#     data = cur.fetchone()
#     cur.close()
#     count = cur.rowcount
#     if count == 0:
#         flash("Users Not Found...!!!!", "danger")
#     else:
#         return render_template("user_profile.html",res=data)
#
# @app.route("/update_user",methods=['GET','POST'])
# def update_user():
#     if request.method == 'POST':
#         name = request.form['name']
#         password = request.form['password']
#         age = request.form['age']
#         address = request.form['address']
#         contact = request.form['contact']
#         mail = request.form['mail']
#         pid=session["pid"]
#         cur = mysql.connection.cursor()
#         cur.execute("update users set name=%s,password=%s,age=%s,address=%s,contact=%s,mail=%s where pid=%s",[name,password,age,address,contact,mail,pid])
#         mysql.connection.commit()
#         flash('User Updated Successfully', 'success')
#         return redirect(url_for('user_profile'))
#     return render_template("user_profile.html")
#
# @app.route("/view_users")
# def view_users():
#     cur = mysql.connection.cursor()
#     qry = "select * from users"
#     cur.execute(qry)
#     data = cur.fetchall()
#     cur.close()
#     count = cur.rowcount
#     if count == 0:
#         flash("Users Not Found...!!!!", "danger")
#     return render_template("view_users.html",res=data)
#
#
# @app.route("/delete_users/<string:id>", methods=['GET', 'POST'])
# def delete_users(id):
#     cur = mysql.connection.cursor()
#     cur.execute("delete from users where pid=%s", [id])
#     mysql.connection.commit()
#     flash("Users Deleted Successfully", "danger")
#     return redirect(url_for("view_users"))
#
# @app.route("/admin_home")
# def admin_home():
#     return render_template("admin_home.html")
#
# @app.route("/user_home")
# def user_home():
# 	return render_template("user_home.html")
#
#
# @app.route("/logout")
# def logout():
#     session.clear()
#     return redirect(url_for("index"))
#
# if(__name__=='__main__'):
#     app.secret_key = '123'
#     app.run(debug=True)