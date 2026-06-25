from debug.response_debug import write_request_json
from openai import OpenAI
from common import *

class touch:

    def __init__(self, url, key, model, msg, temperature=0, max_tokens=2048):
        self.url         = url
        self.key         = key
        self.model       = model
        self.temperature = temperature
        self.max_tokens  = max_tokens
        self.msg         = msg
        self.resultdict  = None
        self.reply       = ''

    def request(self):
        
        client = OpenAI(
            api_key=self.key,
            base_url=self.url
            )

        resp = client.chat.completions.create(
            model=self.model,
            messages=self.msg,
            temperature=self.temperature,
            stream=False,
            extra_body={"thinking": {"type": "disabled"}},
            response_format={'type':'json_object'}
        )

        respdict = resp.model_dump()
        write_request_json(respdict)
        self.resultdict = respdict
        self.reply = self.resultdict['choices'][0]['message']['content']

        with open(ROOT/'debug'/'record.txt','a',encoding='utf-8') as f:
            f.write(self.reply)