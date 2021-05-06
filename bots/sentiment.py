from azure.core.credentials import AzureKeyCredential
from azure.ai.textanalytics import TextAnalyticsClient

endpoint = 'https://sentiment-ner-iki.cognitiveservices.azure.com/'
credential = AzureKeyCredential("cc13e69f62754f878b3e26138383a411")
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

