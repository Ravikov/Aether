import json
from common import *

def write_request_json(resp):
    # OpenAI 返回的是 Pydantic 对象，先转成 dict
    with open(response_json_path,'w',encoding='utf-8') as f:
        json.dump(resp, f, ensure_ascii=False, indent=2)