# 入口函数

"""
通过多次调用配合自模拟自审查自优化方式实现提示词蒸馏

change log:

26.6.24 ravikov
实现基础的请求功能,主循环体闭合

"""

from core.manager import manager
from common import *

distill_manager = manager()

distill_data   = input("请输入蒸馏原料\n>>>")
distill_name   = input("请输入蒸馏原料中蒸馏对象的昵称\n>>>")
score_standard = input("请输入分数要求\n>>>")

try:
    distill_manager.start()
except KeyboardInterrupt:
    pass