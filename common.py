import pathlib

ROOT = pathlib.Path(__file__).parent
response_json_path = ROOT/'debug'/'response.json'
config_path        = ROOT/'config'/'config.json'
prompt_file        = ROOT/'out'/'prompt.md'

distill_name       = ''
distill_data       = {'type':1,'text':''}
test_time          = 5
score_standard     = 80