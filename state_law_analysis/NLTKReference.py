
#%%
import re
import string
from nltk.stem import WordNetLemmatizer
lemmatizer = WordNetLemmatizer()
from nltk.corpus import wordnet
from nltk import pos_tag
#import gensim
#from gensim import corpora, models
from nltk.corpus import stopwords 

class etl_step:
    name="etl_step"
class extract(etl_step):
    def fromMONGODB(self,host,portnumber,dbname,collectionname,expression=None):
        import pymongo
        client = pymongo.MongoClient(host, portnumber)
        tmp_database = client[dbname]
        tmp_collection=tmp_database[collectionname]
        data = list()
        if expression:
            for document in tmp_collection.find(expression):  
                data.append(document)
            return data
        for document in tmp_collection.find():  
                data.append(document)
        return data
    
class load(etl_step):
    def toMONGODB(self,data,host,portnumber,dbname,collectionname):
        import pymongo
        client = pymongo.MongoClient(host, portnumber)
        tmp_database = client[dbname]
        tmp_collection=tmp_database[collectionname]
        results_id=tmp_collection.insert_many(data)
        return results_id 
    
def tokenize(text,text_id,line_id=0):
    #text = re.sub("[^a-zA-Z]"," ", str(text))
    token_counter= 0
    data = list()
    l = [item for item in map(str.strip, re.split("(\W)",text)) if len(item)>0]
    for token in l:
        lower_token = token.lower()

        row ={
              "textID":text_id,
              "lineID":'L00000'+str(line_id),
              "tokenID":'T000000'+str(token_counter),
              "tokenRaw":token,
              "tokenLower":lower_token
             }
        data.append(row)
        token_counter=token_counter+1
    return data
def tokenize_many(data,key_id,key_text):
    new_data=list()
    for row in data:
        d = tokenize(text=row[key_text],text_id=row[key_id])
        if d is None or len(d)<1:
            continue
        new_data = new_data+d
    return new_data
def lemmatize(data,key):
    new_data=list()
    for row in data:
        lower_token = row[key]     
        lemmatized_token_n = wordnet.morphy(lower_token,pos="n")
        lemmatized_token_v = wordnet.morphy(lower_token,pos="v")
        lemmatized_token_a = wordnet.morphy(lower_token,pos="a")
        token=""
        if lemmatized_token_v is not None:
            token= lemmatized_token_v
        elif lemmatized_token_n is not None:
            token= lemmatized_token_n
        elif lemmatized_token_a is not None:
            token= lemmatized_token_a
        else:
            token = lower_token
            
        temp2= pos_tag([token])
        temp2 =temp2[0]
        t,token_type = temp2
        temp = row.copy()
        new_row ={
              "tokenLemmatized_n":lemmatized_token_n,
              "tokenLemmatized_v":lemmatized_token_v,
              "tokenLemmatized_a":lemmatized_token_a,
               "tokenFinal":token,
               "tokenFinalType":token_type
             }
        temp.update(new_row)
        #print(temp)
        new_data.append(temp)
    return new_data    
def prep_dict(vocabulary):
    temp = dict()
    for word in vocabulary:
        temp[word]=0
    return temp

from pprint import pprint      
extract = extract()
load = load()
print("extract data")
data =extract.fromMONGODB(host="localhost",portnumber=27017,dbname="amazon_reviews",
                         collectionname="musical_instruments")
##*********IMPORTANT: SET TO 1000 if to only limit the process to 1000 documents
data = data[0:1000]
print(len(data))
step = 1000
print("start tokenization/lemmatization")
for i in range(0,len(data),step):
    print(i)
    temp = data[i:i+step]
    d = tokenize_many(temp,'_id','reviewText')
    load.toMONGODB(d,host="localhost",portnumber=27017,dbname="amazon_reviews",
                         collectionname="musical_instruments_tokenized")
    new_data= lemmatize(d,'tokenLower')
    load.toMONGODB(new_data,host="localhost",portnumber=27017,dbname="amazon_reviews",
                         collectionname="musical_instruments_lemmatized")
print("tokenization/lemmatization complete")


#%%
data =extract.fromMONGODB(host="localhost",portnumber=27017,dbname="amazon_reviews",
                         collectionname="musical_instruments_lemmatized")

document_matrix_term = dict()
for row in data:
    textID = str(row['textID'])
    token = row['tokenFinal']
    if token in stopwords.words('english'):
        #print(token)
        continue
    list_of_tokens = list()
    if textID in document_matrix_term:
        list_of_tokens = document_matrix_term[textID]
    list_of_tokens.append(token)
    document_matrix_term[textID] = list_of_tokens 
    
processed_docs = list()
for k,v in document_matrix_term.items():
    processed_docs.append(v)
    
dictionary = gensim.corpora.Dictionary(processed_docs)

bow_corpus = [dictionary.doc2bow(doc) for doc in processed_docs]

#bow_doc = bow_corpus[0]
#for i in range(len(bow_doc)):
#    print("Word {} (\"{}\") appears {} time.".format(bow_doc[i][0], 
#                                               dictionary[bow_doc[i][0]], bow_doc[i][1]))
    
tfidf = models.TfidfModel(bow_corpus)
corpus_tfidf = tfidf[bow_corpus]
from pprint import pprint
#for doc in corpus_tfidf:
#    pprint(doc)
#    break
print("LDA Started")
#lda_model = gensim.models.LdaMulticore(bow_corpus, num_topics=20, id2word=dictionary, passes=4, workers=4) 
#for idx, topic in lda_model.print_topics(-1):
#    print('Topic: {} \nWords: {}'.format(idx, topic))
#print("LDA Complete ")
#for index, score in sorted(lda_model[bow_corpus[2]], key=lambda tup: -1*tup[1]):
#    print("\nScore: {}\t \nTopic: {}".format(score, lda_model.print_topic(index, 10)))

lda_model_tfidf = gensim.models.LdaMulticore(corpus_tfidf, num_topics=10, id2word=dictionary, passes=4, workers=4)
for idx, topic in lda_model_tfidf.print_topics(-1):
    print('Topic: {} Word: {}'.format(idx, topic))
for index, score in sorted(lda_model_tfidf[bow_corpus[0]], key=lambda tup: -1*tup[1]):
    print("\nScore: {}\t \nTopic: {}".format(score, lda_model_tfidf.print_topic(index, 10)))
    
    
unseen_document = dict()
unseen_document['reviewText']="""for the first week i used this tea maker it was great... today however, the extremely thin glass pitcher handle came off in my hand... with a freshly brewed pitcher of tea in it... needless to say, the glass and tea hit the floor and my feet... and the pitcher handle was still in my hand.... a couple of small cuts... but this could have been so much worse!!! my grandson (5 yrs) was standing just a few feet from me.... definitely watch the pitcher and be very careful... i followed the recommended brewing directions .... the pitcher is just very thin and not safe... the tea maker is easy to use and the tea tastes great!
"""
unseen_document['textID']="TAFSDFSFSF"

d = tokenize(unseen_document['reviewText'],unseen_document['textID'])
#print(d)
new_d= lemmatize(d,'tokenLower')
list_of_tokens = [row['tokenFinal']   for row in new_d if row['tokenFinal'] not in stopwords.words('english')]

print(list_of_tokens)
bow_vector = dictionary.doc2bow(list_of_tokens)
for index, score in sorted(lda_model[bow_vector], key=lambda tup: -1*tup[1]):
    print("Score: {}\t Topic: {}".format(score, lda_model.print_topic(index, 5)))

