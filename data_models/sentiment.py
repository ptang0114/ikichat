from azure.core.credentials import AzureKeyCredential
from azure.ai.textanalytics import TextAnalyticsClient

endpoint = 'https://iki-sentiment.cognitiveservices.azure.com/'
credential = AzureKeyCredential("3133eaeecd32496284c47454e9b3fd1e")
text_analytics_client = TextAnalyticsClient(endpoint=endpoint, credential=credential)

def senti(sentence):
    sent= [
    {
      "language": "zh-hans",
      "id": "1",
      "text": sentence
    }]
    result = text_analytics_client.analyze_sentiment(sent)
    s = ''.join([doc.sentiment for doc in result if not doc.is_error])
    sentiment = {'sentiment': s}
    return sentiment

def ner(sentence):
    sent= [
    {
      "language": "zh-hans",
      "id": "1",
      "text": sentence
    }]
    results = text_analytics_client.recognize_entities(sent)
    results = [review for review in results if not review.is_error]
    relative = {}
    for result in results:
        for entity in result.entities:
            if entity.category =="PersonType":
                person = entity.text
                if person[0] == '我':
                    relative['person_type'] = person[1:]
                elif len(person) == 1:
                    relative['person_type'] = person+person
                else:
                    relative['person_type'] = entity.text
            else:
                pass
    return relative



