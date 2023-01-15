# importing necessary libraries
import os # allows to get environment variables that store sensitive information such as API keys in a separate secret files
import telebot #allows to create telegram chatbots
import flask # Flask is an open source Python web framework
import requests # used to send HTTP requests
from bs4 import BeautifulSoup # allows to parse the website

# secret files hidden with heroku config
TOKEN = os.environ["TOKEN"]
NAME = os.environ["NAME"]
HEADERS = os.environ["HEADERS"]

headers = {'User-Agent': HEADERS}
bot = telebot.TeleBot(TOKEN, parse_mode=None)
bot.remove_webhook() # empting the url parameter to avoid errors
bot.set_webhook(url=f"https://{NAME}.herokuapp.com/bot") # webhook supplies Telegram with a location, on which our bot listens for updates
doc = requests.get('https://www.cimec.unitn.it/en', headers=headers) #  retrieve data from the website
soup = BeautifulSoup(doc.text, 'html.parser') 
app = flask.Flask(__name__) #starting using flask


# function to crawl data from the cimec site
def handle_posts(path):
    posts_list = []
    posts = path.find_all(attrs="view-content")[0].find_all("a") #finds all headers which are marked 'a' in hlml site structure
    for post in posts:
        posts_list.append(post.text.strip() + f"\n<i>Read more:\t <a href='{post['href']}'>link</a></i>" + "\n\n") #creating the list of links
    return posts_list


# function that is called upon the launch of the bot and when the /start command is typed
@bot.message_handler(commands=['start'])
def start_message(message):
    reply = "Hello! This bot give you some information of CIMeC's latest news or events. To get the latest news type " \
            "/news. To get the events type /events.\nType /help for the list of commands."
    bot.send_message(message.chat.id, reply)


# function that is called when the /help command is typed
@bot.message_handler(commands=['help'])
def help_message(message):
    reply = "type /start to get the description\ntype /news to get the latest news\ntype /events to get the latest news"
    bot.send_message(message.chat.id, reply)


# function that is called when the /news command is typed. Makes a list of the latest cimec news.
@bot.message_handler(commands=['news'])
def news_message(message):
    news_html = soup.find(text="News").parent.next_sibling.next_sibling  # returns the next tag under the same parent.
    news_list = handle_posts(news_html)
    bot.send_message(message.chat.id, "".join(news_list), parse_mode="HTML")


# function that is called when the /events command is typed. Makes a list of the latest cimec events.
@bot.message_handler(commands=['events'])
def events_message(message):
    event_html = soup.find("h2", text="Events").parent
    events_list = handle_posts(event_html)
    bot.send_message(message.chat.id, "".join(events_list), parse_mode="HTML")


# function that is called in all other cases
@bot.message_handler(func=lambda m: True) # echoes all incoming text messages back to the sender. It uses a lambda function to test a message
def echo_all(message):
    reply = "Sorry, I did not understand what you said. Try typing /help for the list of commands or /start to go to " \
            "the beginning "
    bot.send_message(message.chat.id, reply)


# function to create the bot page
@app.route("/bot", methods=['POST'])
def webhook():
    if flask.request.headers.get('content-type') == 'application/json':
        json_string = flask.request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return ''
    else:
        flask.abort(403)


# for the bot to work on heroku
if __name__ == '__main__':
    app.debug = True
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
