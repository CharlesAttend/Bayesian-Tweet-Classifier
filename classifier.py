# -*- coding: utf-8 -*-

def get_data(fname):
    """
    fname : Nom du ficher
    Retourne une liste de chaque ligne du fichier
    """
    l = list()
    with open(fname, "r", encoding="utf8") as f:
        for lines in f:
            l.append(lines.strip())
    return l

def split_data(data):
    """
    data : liste de tweet sous la forme data[i] = 'label, "Tweet"'
    Retourne deux listes: tweet et label avec :
        tweet[i] = le tweet associé à la ligne data[i]
        label[i] = le label associé à la ligne data[i]
    """
    tweet, label = [], []
    for i in data:
        l = i.split(",")
        label.append(l[0].strip())
        tweet.append(l[1].strip())
    return tweet, label

def filter_data(mots, occur):
    """
    mots: liste de mots 
    occur: liste d'occurences du mots[i] associé

    Filtre chaque mot dans mots (stopword, @tag, http link) 
    Et traite également les ponctutions
    """
    stop_word = get_data("stop-word.txt")
    i=0

    while i<len(mots):
        mot = mots[i].lower()
    #On vire les tags et les link
        if mot.startswith("@") or mot.startswith("http"):
            mots.pop(i)
            occur.pop(i)
    #Les stops words
        elif mot in stop_word:
            mots.pop(i)
            occur.pop(i)
    #On filtre les "." et check si il y a des ".." ou "..." si oui on créer un nouveaux mot
    #J'ai remarqué qu'ils ne séparaient jamais les "?!;" par des espaces so je les filtres ici aussi
        elif mot[-1:] in [".","?","!",";",":"]:
            p = detecte_la_ponctuation(mot)
            #Si il y a "???" alors je l'ajoute en tant que nouveau mot ou augmente son nb occur
            if p:     
                try:
                    n = mots.index(p)
                    occur[i] += 1
                except:
                    mots.append(p)
                    occur.append(1)
            else:                       #sinon je suprime simplement le "?" à la fin
                mots[i] = mots[i][:-1]
                i = i-1                 #Je reteste le mot pour éliminer les "fyou!?!?!" ==> "fyou"
        i+=1

def detecte_la_ponctuation(mot):
    """
    Teste si le mot se termine par plus d'une ponctuation (exemple: "????", "!!!!") et retourne celle-ci 
    Sinon retourne False 
    """
    p = mot[-1:]
    i = len(mot)-2                  #Ici -2 car la première lettre a déjà été testé dans la fonction précédente  
    try:
        while mot[i] in [".","?","!",";",":"]:
            if mot[-i-1:] == p*(i+1):
                p = p*(i+1)
            i -= 1
        else:                       #Si c'est vrai (cad que la boucle s'est executé) alors je retourne p (qui est donc au minimum '??')
            return p
    except IndexError:              #Pour gérer les "..." ou "????" qui arrivent en tant que mot seul
        return mot 
    return False                    #Si la boucle ne s'excute pas alors je retourne False, uniquement la premère lettre est une ponctuation



def all_words(tweets_list):
    """
    tweets_list: Liste de tweets à traiter

    Retourne 3 listes: 
        wordS: Liste de tous les mots de tous les tweets de tweets_list
        occur: Liste d'occurence de chanque mot de chaque tweet de tweets_list
        n_corp: Nombre de mot dans tous les tweets de tweets_list
    """
    wordS, occur, n_corp = list(), list(), 0
    for tweet in tweets_list:
        phrase = tweet.split(" ")
        for i in range(len(phrase)):#Pour chaque mot
            n_corp += 1 #je le compte 
            word = phrase[i]
            if word in wordS: #Si ce mot est déjà dans wordS
                occur[wordS.index(word)] += 1 #J'incrémente occur
            else: #sinon je l'ajoute
                wordS.append(word)
                occur.append(1)
    return wordS, occur, n_corp

#PARTIE 3 - CLASSIFICATION
def clas(tweet_list, mots_corp, p_m, mots_pos, p_m_pos, mots_neg, p_m_neg):
    """
    tweet_list: Liste de tweet à tester

    mots_corp: Liste de mot du corpus de train
    p_m: Liste des probabilités de chaque mot du corpus train

    mots_pos: Liste de mot "positif"
    p_m_pos: Liste des probabilités de chaque mot "positif"
    mots_neg: Liste de mot "négatif"
    p_m_neg: Liste des probabilités de chaque mot "négatif"

    Retourne un liste prédiction ou prediction[i] est associé à la prédiction(Positive ou négative) de tweet_list[i]
    """
    prediction = list()
    for tweet in tweet_list:
        tweet = tweet.split(" ")
        tmp_m_pos = 1
        tmp_m_neg = 1
        tmp_m = 1
        for word in tweet:
            try:                                                            #Si c'est possible on calcule 
                tmp_m = tmp_m * p_m[mots_corp.index(word)]                  #le produit pour l'utiliser dans la formule
                tmp_m_pos = tmp_m_pos * p_m_pos[mots_pos.index(word)]
                tmp_m_neg = tmp_m_neg * p_m_neg[mots_neg.indes(word)]
            except:
                continue
        p_neg_m = (p_neg * tmp_m_neg)/tmp_m
        p_pos_m = (p_pos * tmp_m_pos)/tmp_m
        if p_neg_m < p_pos_m:
            prediction.append("positive")
        else:
            prediction.append("negative")
    return prediction

def score(prediction, label):
    """
    Fonction scrore : regarde si chaque prédiction est correct, si oui incrémente le score
    """
    score = 0
    for i in range(len(label)):
        if prediction[i] == label[i]:
            score += 1
    return score

#PARTIE 1 - PRÉPARATIONS 
#Lecture des fichiers dev et test et train
tweets_dev, label_dev = split_data(get_data("tweets_dev.csv"))
tweets_test, label_test = split_data(get_data("tweets_test.csv"))
tweets_train, label_train= split_data(get_data("tweets_train.csv"))

#PARTIE 2 - APPRENTISSAGE 
#séparation des tweets dans deux listes "pos" et "neg" en fonction du label.
neg, pos = list(), list()
for i in range(len(label_train)):
    if label_train[i] == "positive":
        pos.append(tweets_train[i])
    else:
        neg.append(tweets_train[i])

#Création des listes de mots 
mots_corp, occur_corp, n_corp = all_words(tweets_train)
mots_pos, occur_pos, n_pos = all_words(pos)
mots_neg, occur_neg, n_neg = all_words(neg)

#Enlever les stop-words
filter_data(mots_corp, occur_corp)
filter_data(mots_pos, occur_pos)
filter_data(mots_neg, occur_neg)

#Calcule des probabilitées qui nous serons utile dans la formule de Bayés
p_pos = len(pos)/(len(pos)+len(neg))    #Proba d'un commentaire positif
p_neg = 1-p_pos                         #Proba d'un commentaire négatif
p_m = list()                            #Proba d'un mot dans le corps 
for i in range(len(occur_corp)):
    p_m.append(occur_corp[i]/n_corp)
p_m_pos = list()                        #Proba d'un mot dans le corps postif
for i in range(len(occur_pos)):
    p_m_pos.append(occur_pos[i]/n_pos)
p_m_neg = list()                        #Proba d'un mot dans le corps négatif
for i in range(len(occur_neg)):
    p_m_neg.append(occur_neg[i]/n_neg)

#Test pour le Dev Set
prediction = clas(tweets_dev, mots_corp, p_m, mots_pos, p_m_pos, mots_neg, p_m_neg)
scoree = score(prediction, label_dev)
print(scoree, "sur", len(tweets_dev), "=>","Score of correct prediction on dev set" ,scoree/len(tweets_dev))

#Test pour le Tweets Set
prediction = clas(tweets_test, mots_corp, p_m, mots_pos, p_m_pos, mots_neg, p_m_neg)
scoree = score(prediction, label_test)
print(scoree, "sur", len(tweets_test), "=>", "Score of correct prediction on test set", scoree/len(tweets_test))