import requests
from pprint import pprint

class AzureTextAnalytics:
    sub_key = 'defe981ca98e445ebb18e524edf78532'
    base_url = "https://westcentralus.api.cognitive.microsoft.com/text/analytics/v2.0/"
    headers = {"Ocp-Apim-Subscription-Key": sub_key}
    
    def get_language(self,document):
        language_url = self.base_url + "languages"
        
        languages = dict()

        try:
            response = requests.post(language_url,headers=self.headers,json=document)
            languages = response.json()
        except:
            languages["errors"] = ["""An error has occured. Please follow the document format described in 
            https://docs.microsoft.com/en-us/azure/cognitive-services/text-analytics/quickstarts/python"""]
        
        return languages
    
    def get_sentiment(self,document):
        sentiment_url = self.base_url + "sentiment"
            

documents = { 'documents': [
    { 'id': '1', 'text': 'This is a document written in English.' },
    { 'id': '2', 'text': 'Este es un document escrito en Español.' },
    { 'id': '3', 'text': '这是一个用中文写的文件' }
]}

# AzureTextAnalytics.get_language(documents)

tst = AzureTextAnalytics()
pprint(tst.get_language(documents))
