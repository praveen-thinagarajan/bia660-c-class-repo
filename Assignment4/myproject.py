import os
import json
import requests
from flask import Flask, request, Response
import requests
import datetime
from collections import defaultdict
import fuzzywuzzy
import numpy
import random
import time
from fuzzywuzzy import fuzz
import re
import pyowm

application = Flask(__name__)

#SLACK_WEBHOOK_SECRET = os.environ.get('SLACK_WEBHOOK_SECRET')
# BOT_CHAT group
slack_inbound_url = 'https://hooks.slack.com/services/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'
# BOTS_TESTING_PRAVEEN group
# slack_inbound_url = 'https://hooks.slack.com/services/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'

@application.route('/slack', methods=['POST'])
def inbound():
    # Adding a delay so that all bots don't answer at once (could overload the API).
    # This will randomly choose a value between 0 and 10 using a uniform distribution.
    delay = random.uniform(0, 10)
    time.sleep(delay)

    # Extracting infromation from  messages posted on the slack channel
    response = {'username': 'magic_bot', 'icon_emoji': ':sparkles:'}
    channel = request.form.get('channel_name')
    username = request.form.get('user_name')
    text = request.form.get('text')
    inbound_message = username + " in " + channel + " says: " + text
    owner_name = 'praveen_thinagarajan'
    my_chatbot_name = 'magic_bot' 
    bot_response = '&lt;BOTS_RESPOND&gt;'
    code_help = '&lt;I_NEED_HELP_WITH_CODING&gt;'
    weather_update = '&lt;WHAT\'S_THE_WEATHER_LIKE_AT&gt;'

    # Checking if the user who sends the message is within a approved list of users
    if username != my_chatbot_name and username in [owner_name, 'zac.wentzell']:
        # **************************Task-1*****************************************************************
        if text == bot_response:
            response['text'] = 'Hello, my name is ' + my_chatbot_name + '. I belong to ' + owner_name+'. I live at 35.166.143.111.'
            r = requests.post(slack_inbound_url, json=response)

        # **************************Task-2 and Task-3*****************************************************************
        if text.split(':')[0] in [code_help]:
            sub_text = str(text).split(':')
            question = sub_text[1]

            # Check if the query string has specific TAGGED names
            # Changing set of parameters to be sent to Stackoverflow API if TAGGED names are required in search
            if list(re.findall(r'\[([^]]*)\]',text)).__len__() > 0:
                question = sub_text[1].split('[')[0]
                tagged_list = re.findall(r'\[([^]]*)\]',text)
                # if list(tagged_list).__len__() > 0:
                categories_search = {'order': 'desc', 'sort': 'activity', 'q': question, 'tagged':tagged_list, 'site': 'stackoverflow'}

            # Changing set of parameters to be sent to Stackoverflow API if TAGGED names are not required in search
            else:
                categories_search = {'order': 'desc', 'sort': 'activity', 'q': question, 'site': 'stackoverflow'}

            # Invoking Stackoverflow API to search for results
            r = requests.get('https://api.stackexchange.com/2.2/search/advanced', params=categories_search)
            json_text = r.json()
            json_all_site_items = json_text.get("items");
            # Examine each test result based on search result title
            items_dicts = defaultdict(str)
            items_metrics = defaultdict(str)
            items_link_texts_fuzzy = defaultdict(str)
            item_index = 0
            for dict_item in json_all_site_items:
                metrics_list = []
                items_dicts[item_index] = dict_item
                item_index += 1
                metrics_list.append(dict_item.get("answer_count"))
                metrics_list.append(dict_item.get("creation_date"))
                metrics_list.append(dict_item.get("link"))
                items_metrics[item_index] = metrics_list
                entry_text = dict_item.get("link").split('/')[
                    len(dict_item.get("link").split('/')) - 1]
                # Making use of FUZZY-WUZZY API to find relevance of search query to the page results
                fuzz_value = fuzzywuzzy.fuzz.ratio(question, entry_text)
                items_link_texts_fuzzy[item_index] = fuzz_value
            # Sort the results based on FUZZY-WUZZY relevance
            items_fuzzy_sorted = sorted(items_link_texts_fuzzy.values(), reverse=True)
            sorted_dicts = defaultdict(str)
            counter = 0
            while len(sorted_dicts.keys()) < 5:
                try:
                    fuzz_value = items_fuzzy_sorted[counter]
                    required_index = [k for k, v in items_link_texts_fuzzy.iteritems() if v == fuzz_value]
                    for entry in required_index:
                        sorted_dicts[counter] = items_metrics[entry]
                        counter += 1
                except:
                    pass

            # Constructing the response message in required format
            message_text = ''
            for entry in sorted_dicts.values():
                if not message_text == '':
                    message_text += '\n'
                creation_date = datetime.datetime.fromtimestamp(entry[1]).strftime("%B %d %Y")
                entry_text = entry[2].split('/')[len(entry[2].split('/')) - 1]
                message_text += entry_text +' ' + '<' + entry[2] + '|' + 'Link' + '>'+' ' + '(' + str(
                    entry[0]) + ' responses) ' + creation_date

            response_2={
                'username': 'magic_bot',
                'icon_emoji': ':sparkles:',
                "attachments": [
                    {
                        "pretext": "There you go! See if these help!",
                        "title":"See Stackoverflow for more results!",
                        "title_link": "http://stackoverflow.com/",
                        "author_name": question,
                        "text" : message_text,
                        "color" : "#7CD197",
                        "footer" : "SlackOverflow Search Results",
                        "footer_icon" : "https://cdn.sstatic.net/Sites/stackoverflow/img/apple-touch-icon@2.png?v=73d79a89bded"

                    }
                ]
            }
            r = requests.post(slack_inbound_url, json=response_2)

        # **************************Task-4*****************************************************************
        elif text.split(':')[0] in [weather_update]:
            # Invoke pyowm API using registered API key
            owm = pyowm.OWM('1dd90cffb7e352cd8bb99f49449e4633')
            location = text.split(':')[1]
            observation = owm.weather_at_place(location)
            w = observation.get_weather()
            # Construct the forecast text for weather update
            forecast_text = "Weather Status: "+str(w.get_detailed_status()).capitalize() + "\n"
            forecast_text += "Temperature: "+str(w.get_temperature('fahrenheit')['temp']) + " " + u'\u00b0' +"F" + "\n"
            forecast_text += "Humidity level: " + str(w.get_humidity()) +"%" + "\n"
            if "gust" in w.get_wind():
                forecast_text += "Wind gust: " + str(w.get_wind()["gust"]) + "\n"
            if "speed" in w.get_wind():
                forecast_text += "Wind speed: " + str(w.get_wind()["speed"]) + " mps" + "\n"
            if "deg" in w.get_wind():
                forecast_text += "Wind degree: " + str(w.get_wind()["deg"]) + " "+ u'\u00b0' + "\n"
            forecast_text += "Temperature Max degree: " + str(w.get_temperature('fahrenheit')['temp_max']) +  " "+ u'\u00b0' + 'F' + "\n"
            forecast_text += "Temperature Min degree: " + str(w.get_temperature('fahrenheit')['temp_min']) +  " "+ u'\u00b0' + 'F' + "\n"

            # Constructing location string for image link URL
            location_split=str(location).split(' ')
            location_string = ""
            for lit in location_split:
                location_string += lit
            # Constructing image link string
            image_link = "https://maps.googleapis.com/maps/api/staticmap?center="+location_string+"&zoom=13&size=600x300&maptype=roadmap&key=AIzaSyCIWOwg-Y88t8-MJMvQ1QHbS7ZjQYE9xFE"
            response_3 = {
                'username': 'magic_bot',
                'icon_emoji': ':sparkles:',
                "attachments": [
                    {
                        "pretext": "Weather update for you!",
                        "title": "Check the weather site for detailed results!",
                        "title_link": "https://weather.com/",
                        "author_name": location,
                        "text": forecast_text,
                        "image_url": image_link,
                        "color": "#7CD197",
                        "footer": "Weather updates from OpenWeatherMap",
                        "footer_icon": "https://upload.wikimedia.org/wikipedia/commons/1/15/OpenWeatherMap_logo.png"

                    }
                ]
            }
            r = requests.post(slack_inbound_url, json=response_3)
        # Testing if no proper inputs are given
        # else:
        #     response['text'] = "Sorry I didn't get that. How can I help you? :"
        #     response['pretext'] = "pretext"
        #     response['color'] = "#7CD197"
        #     r = requests.post(slack_inbound_url, json=response)


    print inbound_message
    print request.form
    return Response(), 200
	      
@application.route('/', methods=['GET'])
def test():
    return Response('It works!')


if __name__ == "__main__":
    application.run(host='0.0.0.0', port=41953)

