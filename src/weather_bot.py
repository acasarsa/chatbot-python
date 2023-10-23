import os
import spacy
import requests

nlp = spacy.load("en_core_web_lg")


def get_weather(city_name):
    api_key = os.environ.get('OPEN_WEATHER_BOT_API_KEY')
    if not api_key:
        print('API Key not set.')
        return None

    api_url = "http://api.openweathermap.org/data/2.5/weather?q={}&units=imperial&appid={}".format(city_name, api_key)

    response = requests.get(api_url)
    if response.status_code != 200:
        print('[!] HTTP {0} calling [{1}]'.format(response.status_code, api_url))
        return None

    response_dict = response.json()
    # Ensure the keys are in the response
    if "main" in response_dict and "weather" in response_dict:
        full_temp = response_dict["main"]["temp"]
        temp = round(full_temp)
        description = response_dict["weather"][0]["description"]
        return f"In {city_name.capitalize()}, the current weather is: {temp}F with {description}"
    else:
        print('Unexpected response format.')
        return None


def chatbot(statement):
    weather = nlp("Current temperature and weather description in a city")
    statement = nlp(statement)
    min_similarity = 0.5

    if weather.similarity(statement) >= min_similarity:
        for ent in statement.ents:
            if ent.label_ == "GPE":  # GeoPolitical Entity
                city = ent.text
                return get_weather(city) or "Something went wrong."
        return "You need to tell me a city to check."
    else:
        # if weather.similarity(statement) >= min_similarity is not sufficient ask for rephrase
        return "I'm sorry, I can only provide information about the weather."

# Using the app as it currently exists
# response = chatbot("How hot is it in Brooklyn today?")
# print(response)
