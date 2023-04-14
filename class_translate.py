import requests, uuid, json
from settings import KEY, REGION, GOOGLE 


class Translate:
    
    def __init__(self, text, target_language, sourse_language):
        self.text = text
        self.target_language = target_language
        self.sourse_language = sourse_language
        self.url = {'Google': 'https://translation.googleapis.com/language/translate/v2',
                    'Microsoft': 'https://api.cognitive.microsofttranslator.com/translate'}
                   
    def post(self, *args, **kwargs):
        request = requests.post(*args, **kwargs)
        response = request.json()
        answer = json.dumps(response, ensure_ascii=False)
        return json.loads(answer)    
    
    def google_translate(self):
        params = {
            'q': self.text,
            'target': self.target_language,
            'sourse': self.sourse_language,
            'key': GOOGLE
            }        
        request = self.post(self.url.get('Google'), params=params)
        
        for r in request['data']['translations']:            
            if r['detectedSourceLanguage'] == self.sourse_language:
                return r['translatedText']                            
            else:
                return "Invalid input language" 
            
        for r in request['data']['translations']:
            if r['translatedText'] == None:
                return self.azure_translate()
                               
    
    def azure_translate(self):
        params = {
            'api-version': '3.0',
            'from': self.sourse_language, 
            'to': self.target_language
        }
        headers = {
            'Ocp-Apim-Subscription-Key': KEY,
            'Ocp-Apim-Subscription-Region': REGION,
            'Content-type': 'application/json',
            'X-ClientTraceId': str(uuid.uuid4())
        }
        body = [{
            'text': self.text
        }]
        request = self.post(self.url.get('Microsoft'), params=params, headers=headers, json=body)
        return request    

tr1 = Translate('Something else', 'uk', 'en')
print(tr1.google_translate())