import pandas as pd
from bs4 import BeautifulSoup as bs
import requests
import streamlit as st
from streamlit_option_menu import option_menu

#Fonction de résumé
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from heapq import nlargest
from newspaper import Article

sidebar_custom_style = """
<style>
[data-testid="stSidebar"] {
    background-color: lightcyan;
}
.stOptionMenu {
    border-radius: 20px;
    padding: 20px;
    background-color: white;
}
.style{
    color: darkblue;
}
"""

# Afficher le style personnalisé dans la sidebar
st.markdown(sidebar_custom_style, unsafe_allow_html=True)

import pandas as pd

with st.sidebar:
    selected = option_menu(
        menu_title='Menu',
        options=['A Propos','Sites Web'])
    
if selected == 'A Propos':
    st.write("Présentation du fonctionnement")

elif selected == 'Sites Web':
    option_submenu = st.sidebar.radio('Sites Web', ('Retaildive.com',
                                                    'autres ajout en cours'))
    
    if option_submenu =='Retaildive.com':
        st.write("salut")
        st.write('Titre et Résumé')
        st.write("Merci de patienter pendant la récupération des résumés")
        
        nltk.download('punkt')
        nltk.download('stopwords')

        def summarize(text, n=5):
            sentences = sent_tokenize(text)
            words = word_tokenize(text.lower())
            stop_words = set(stopwords.words('english'))  # Changez 'english' si vous travaillez dans une autre langue
            word_freq = {}

            for word in words:
                if word not in stop_words:
                    if word not in word_freq:
                        word_freq[word] = 1
                    else:
                        word_freq[word] += 1

            max_freq = max(word_freq.values())

            for word in word_freq.keys():
                word_freq[word] = (word_freq[word] / max_freq)

            sent_scores = {}
            for sentence in sentences:
                for word in word_tokenize(sentence.lower()):
                    if word in word_freq.keys():
                        if len(sentence.split(' ')) < 30:  # Limitez la longueur des phrases pour éviter les résumés trop longs
                            if sentence not in sent_scores.keys():
                                sent_scores[sentence] = word_freq[word]
                            else:
                                sent_scores[sentence] += word_freq[word]

            summary_sentences = nlargest(n, sent_scores, key=sent_scores.get)
            summary = ' '.join(summary_sentences)
            return summary

        ###########################################################################

        url = 'https://www.retaildive.com'
        page = requests.get(url)

        soup = bs(page.text, 'lxml')

        divs = soup.find_all('div',class_="medium-8 columns")
        list_lien=[]
        for div in divs:
            a = div.find('a')
            list_lien.append(a['href'])

                #Création d'un Dataframe
            df = pd.DataFrame({'liens':list_lien})
            df['Debut']='https://www.retaildive.com'
            df['lien'] = df['Debut']+df['liens']

                #utilisation de la fonction
        liste_resume=[] 
        for i in df['lien']:
            article = Article(i)
            article.download()
            article.parse()
            article.nlp()
            text = article.text
            resume_lien = summarize(text)
            titre = article.title
            liste_resume.append({"Titre Article":titre,
                                 "Résumé Article":resume_lien})
           
        resume = pd.DataFrame(liste_resume)
        
        # Créer une application Streamlit
        st.title('Résumés d\'articles')

# Afficher les titres et les résumés dans une boucle for
        for index, row in resume.iterrows():
            st.header(row['Titre Article'])
            st.write(row['Résumé Article'])