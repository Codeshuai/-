from flask import Flask, request, jsonify
from test import Answer

app = Flask(__name__)

# 定义返回消息的函数
# @app.route('/send', methods=['POST'])
# def send():
#     query = request.json.get('inputMsg', '')
#     answer = Answer(query)
#     if answer:
#         return answer
#     else:
#         return jsonify({"Answer": "服务器出错了,Gpt无回答！"})

@app.route('/send', methods=['POST'])
def send():
    query = request.get_json()
    answer = Answer(query)
    #answer是json文件
    return answer


if __name__ == '__main__':
    # app.run(host='127.0.0.1', port=8080)
    app.run()