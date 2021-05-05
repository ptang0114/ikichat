from azure.core.credentials import AzureKeyCredential
from azure.ai.textanalytics import TextAnalyticsClient

endpoint = 'https://iki-sentiment.cognitiveservices.azure.com/'
credential = AzureKeyCredential("3133eaeecd32496284c47454e9b3fd1e")
text_analytics_client = TextAnalyticsClient(endpoint=endpoint, credential=credential)

def sentiment(sentence):
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

