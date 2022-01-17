import translators as ts
from ColorPrint import *

proxy = None

def translate(text):
    text = text.value
    result = ""
    ts_func_list = [ts.alibaba, ts.tencent, ts.google, ts.caiyun]
    ColorPrint.print_bold("Plain: " + text)
    isnt_word = (" " in text) or ("_" in text) or ("/" in text)
    for i, translator in enumerate(ts_func_list):
        try:
            result += "[" + str(translator).split(' ')[2].split('.')[0] + "]\r\n" + translator(text, to_language="zh", if_use_cn_host=True, timeout=3, proxy=proxy) + "\r\n"
        except:
            if i == len(ts_func_list) - 1:
                ColorPrint.print_fail("Translate Failed")
                return
            continue
        if isnt_word:
            break
    ColorPrint.print_pass(result)