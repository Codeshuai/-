from flask import request
# from loguru import logger
from intent_clarification.interaction.run_new import Api_Cubic
import json
from definitions import *

from wx.verification import signature as f_signature	# 签名算法
import wx.receive as receive	# 接收微信消息的地形
import wx.reply as reply		# 将要答复的信息包装成微信需要的xml格式


class WxHandle:

    @staticmethod
    def post():
        """
        响应微信的post请求，微信用户发送的信息会使用Post请求
        :return:
        """
        receive_msg = receive.parse_xml(request.data)
        start_message = ['start', 'Start', 'START', 'hello', 'Hello', '开始', '你好', '您好', '开始吧', '怎么说','你是谁']
        try:
            # logger.info("接收微信消息->\n"+str(request.data))
            # 对微信传来的xml信息进行解析，解析成我们自定义的对象信息
            # 如果解析成功
            if isinstance(receive_msg, receive.Msg):
                # 该微信信息为文本信息
                if receive_msg.type == "text":
                    # 创建一条文本信息准备返回给微信
                    query = receive_msg.usage
                    user_id = receive_msg.fromUser
                    if query in start_message:
                        bot_reply = "请输入您的问题。注意用英文输入。我暂时只能解决与Java API的问题。\n"\
                                    "接下来我会针对您的问题提问并给出推荐选项，请从给出的选项种进行选择并输入。\n选项参考输入格式：\n（1）option\n（2）5.option\n（3）任意输入。不建议此种输入方式，但我会从选项选择最相似的几个作为参考。" \
                                    "如果要开始新的对话请输入：Start a new conversation"
                        msg = reply.TextMsg(receive_msg, bot_reply)
                        return msg.send()
                    else:
                        with open(session_DIR + 'cache.json', 'r') as f:
                            data = json.load(f)
                        if user_id in list(data.keys()):
                            session_history = data[user_id]
                        else:
                            data[user_id] = ""
                            session_history = data[user_id]
                        if query == 'Start a new conversation':
                            data[user_id] = ""
                            with open(session_DIR + 'cache.json', 'w') as f:
                                json.dump(data, f)
                            msg = reply.TextMsg(receive_msg, "Please input your query:")
                            return msg.send()
                        else:
                            input_query = session_history + query
                            q, d, flag = Api_Cubic().wechatbot(input_query)
                            bot_reply = ""
                            if flag == 'recommend':
                                for _, api in enumerate(q):
                                    bot_reply = ' ' + str(_ + 1) + '. API method: ' + api + '\n' + ' API description: ' + d[_] + '\n\n'
                                bot_reply = bot_reply.rstrip('\n\n')
                                data[user_id] = ""
                                with open(session_DIR + 'cache.json', 'w') as f:
                                    json.dump(data, f)
                                recommend_message = '这些API可能对您有帮助：\n'
                                bot_reply = recommend_message + bot_reply
                                msg = reply.TextMsg(receive_msg, bot_reply)
                                return msg.send()
                            else:
                                for idd, option in enumerate(d):
                                    bot_reply = ' ' + bot_reply + str(idd + 1) + ". " + option + "\n"
                                bot_reply = q + '\n' + bot_reply
                                msg = reply.TextMsg(receive_msg, bot_reply)
                                err1 = 'These options may help you:'
                                err2 = 'Your reply seems to be outside the above options.'
                                if err1 not in bot_reply and err2 not in bot_reply:
                                    cache_chat = input_query + '\n' + bot_reply + '=========='
                                    data[user_id] = cache_chat
                                    with open(session_DIR + 'cache.json', 'w') as f:
                                        json.dump(data, f)
                                # 发送我创建的文本信息
                                return msg.send()
                else:
                    # 该信息不为文本信息时，发送我定义好的一条文本信息给他
                    return reply.Msg(receive_msg).send()
        except Exception:
            # logger.error("解析微信XML数据失败！")
            data = {"abc": "abc"}
            with open(session_DIR + 'cache.json', 'w') as f:
                json.dump(data, f)
            print('error')
            msg = reply.TextMsg(receive_msg, "对不起，服务器出错，请重新输入")
            return msg.send()
        return "xml解析出错"

    @staticmethod
    def get():
        """
        响应微信的get请求，微信的验证信息会使用get请求
        这里的验证方式是按照微信公众号文档上的教程来做的
        :return: 
        """
        # 微信传来的签名，需要和我生成的签名进行比对
        signature = request.args.get('signature')   # 微信已经加密好的签名，供我比对用
        timestamp = request.args.get('timestamp')   # 这是我需要的加密信息
        nonce = request.args.get('nonce')           # 也是需要的加密信息
        # 判断该请求是否正常，签名是否匹配
        try:
            # 微信传来的签名与我加密的签名进行比对，成功则返回指定数据给微信
            if signature == f_signature(timestamp, nonce):
                # 微信要求比对成功后返回他传来的echost数据给他
                return request.args.get('echostr')
            else:
                return ""
        except Exception:
            # logger.error("签名失败！")
            print('签名失败！')
        return "签名失败！"