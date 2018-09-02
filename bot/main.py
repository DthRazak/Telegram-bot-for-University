from flask import request
from flask import Flask
from flask import jsonify
from flask_sslify import SSLify
import msgParser as msgPr
import botController as bot

app = Flask(__name__)
sslify = SSLify(app)


@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        r = request.get_json()
        if msgPr.isBotCommand(r):
            bot.manageBotCommand(r)
        elif msgPr.isMainCommand(r):
            bot.manageMainComand(r)
        elif msgPr.isCallbackQuery(r):
            bot.manageCallbackQuery(r)
        else:
            bot.manageSimpleMessage(r)
        return jsonify(r)
    return '<h1>Hello bot</h1>'


if __name__ == '__main__':
    app.run()