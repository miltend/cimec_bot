import os
import telebot
import flask
import requests
from bs4 import BeautifulSoup

TOKEN = os.environ["TOKEN"]

# WEBHOOK_HOST = os.environ["WEBHOOK_HOST"]
# HEADERS = os.environ["HEADERS"]
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Chrome/50.0.2661.102 Safari/537.36'}
# WEBHOOK_URL_BASE = "https://cimecbot.herokuapp.com"


bot = telebot.TeleBot(TOKEN, parse_mode=None)

bot.remove_webhook()
bot.set_webhook(url="https://cimecbot.herokuapp.com/bot")

doc = requests.get('https://www.cimec.unitn.it/en', headers=headers)
soup = BeautifulSoup(doc.text, 'html.parser')
app = flask.Flask(__name__)


def handle_posts(path):
    posts_list = []
    posts = path.find_all(attrs="view-content")[0].find_all("a")
    for post in posts:
        posts_list.append(post.text.strip() + f"\n<i>Read more:\t <a href='{post['href']}'>link</a></i>" + "\n\n")
    return posts_list


@bot.message_handler(commands=['start', 'help'])
def start_message(message):
    description = "Bot description. To get the latest CIMeC news type /news. To get events type /events."
    bot.send_message(message.chat.id, description)


@bot.message_handler(commands=['news'])
def news_message(message):
    news_html = soup.find(text="News").parent.next_sibling.next_sibling
    news_list = handle_posts(news_html)
    bot.send_message(message.chat.id, "".join(news_list), parse_mode="HTML")


@bot.message_handler(commands=['events'])
def events_message(message):
    event_html = soup.find("h2", text="Events").parent
    events_list = handle_posts(event_html)
    bot.send_message(message.chat.id, "".join(events_list), parse_mode="HTML")


@bot.message_handler(func=lambda m: True)
def echo_all(message):
    bot.send_message(message.chat.id, message.text)


@app.route("/bot", methods=['POST'])
def webhook():
    if flask.request.headers.get('content-type') == 'application/json':
        json_string = flask.request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return ''
    else:
        flask.abort(403)

# bot.infinity_polling()


if __name__ == '__main__':
    app.debug = True
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
    # app.run(host='0.0.0.0')
