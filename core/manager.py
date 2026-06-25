import ast
import json

import common
from core.llm_api import touch


def _parse_reply(text):
    return ast.literal_eval(text)


class manager:

    def __init__(self):
        with open(common.config_path,'r',encoding='utf-8') as f:
            self.configdict   = json.load(f)
        self.prompt           = ''     #默认提示词为空
        self.loop             = True   #循环控制
        self.suggest          = ''     #修改建议
        self.loop_n           = 1      #循环次数
        self.chat_test_list   = []     #测试用句
        self.test_result_list = []     #模拟对话列表
        self.toucher          = touch( #API请求器
                                url=self.configdict['api']['url'],
                                key=self.configdict['api']['key'],
                                model=self.configdict['api']['model'],
                                msg='')
        self.checkend         = ''     #对话审查结果
        self.score            = 0      #审查得分
            
    # 提示词生成
    def creat(self):

        reply_format = """
{
'prompt':提示词内容,
'chat_test':以列表形式给出%d句话用于对提示词进行审查测试,测试用句应贴近人类交流语言,就像人类日常对话一样即可
            例如['吃饭没?','你周末有事吗?','那啥,跟你说个事',......]等各种类似语句,不要直接用示例,也不要用蒸馏原料中的语句,
            有时若蒸馏对象语言带有方言特色,你的测试用句里也可以适当模仿,若没有明显的方言特色请你严格按照普通话输出
}
""" % common.test_time
        
        self.toucher.temperature = 0.6
        self.toucher.msg = [{'role':'system','content':f"""
请按照用户所给的提示词要求或蒸馏对象的聊天记录输出合适的提示词(没有原料就直接创造一个人格),以达到蒸馏的目的
提示词应遵守一定的格式,严禁出现格式要求以外的任何回复,比如把性格、说话方式等等项目分类列出,提示词字符串内容以md形式输出;
必须严格遵守的回复格式(json):{reply_format};
蒸馏对象:{common.distill_name}(留空则忽略);
上一轮得分(百分制):{self.score};
上一轮审查修改建议:{self.suggest};
当前提示词:{self.prompt};
迭代次数:{self.loop_n}
"""}]+[{'role':'user','content':f"以下是蒸馏原料:{common.distill_data['text']}"}]

        self.toucher.request()
        parsed = _parse_reply(self.toucher.reply)
        self.prompt = parsed['prompt']
        self.chat_test_list = parsed['chat_test']
        print(f"已生成第{self.loop_n}版提示词")
        self.loop_n += 1
        with open(common.prompt_file,'w',encoding='utf-8') as f:
            f.write(self.prompt)

    # 模拟对话
    def simulation_chat(self):

        self.toucher.temperature = 1.0
        for i in self.chat_test_list:
            print(f"进行交流测试,msg: {i}")
            self.toucher.msg = [
                {'role':'system','content':self.prompt+'\njson格式:{"msg":输出字符串}'},
                {'role':'user','content':i}
                ]
            self.toucher.request()
            result = _parse_reply(self.toucher.reply)
            self.test_result_list.append(
                f"用户:{i}\nAI:{result['msg']}"
                )
            print(f"本轮测试结束,回复: {result}")

    # 模拟对话审查
    def check(self):

        print('开始进行审查...')
        self.toucher.temperature = 0
        self.toucher.msg = [
        {'role':'system','content':"""
请将用户提供的对哈记录(测试提示词的结果,无上下文机制,列表形式)进行审查,将其与蒸馏原料进行对比,确保对话中AI的语言风格与蒸馏
原料中保持一致,并给出打分(0~100分),核心要求:
1.回复应与人类语言风格相似(无限接近),越相似分数越高
2.语言风格必须与蒸馏原料中的风格相近,这一项最为重要
3.你需要给出总体打分与各项分别打分,并以如下json格式回复,并遵守数据类型要求:
{
'whole_score':总体得分,整数,
'human_similar':与人类相似度评分,整数,
'style_similar':语言风格相似度评分,整数,
'fix_suggest':下一步修改建议,分条列出,帮助模型攥写更好的提示词,字符串         
}
4.除非提示词已经达到优秀标准,否则你需要压低分数,给予足够的优化空间
5.这是用户要求的分数:%d,若已完好便可使分数达到要求,程序将结束
""" % common.score_standard },
        {'role':'user','content':f"对话记录:{self.test_result_list}"}
        ]
        
        self.test_result_list = []

        self.toucher.request()
        self.checkend = _parse_reply(self.toucher.reply)
        self.suggest  = self.checkend['fix_suggest']
        self.score    = self.checkend['whole_score']

        print(f"""打分结果:
                总体得分:{self.score}
                类人度得分:{self.checkend['human_similar']}
                风格近似度得分:{self.checkend['style_similar']}
                修改建议:{self.suggest}
""")
        if self.score >= common.score_standard:
            print('分数达到要求标准,循环退出,可在 /out/prompt.md 内查看提示词')
            self.loop = False

    def start(self):

        while self.loop:
            self.creat()
            self.simulation_chat()
            self.check()