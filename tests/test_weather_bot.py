from unittest import TestCase, main, mock
from importlib import reload
from src import weather_bot


class TestGetWeather(TestCase):

    def setUp(self):
        # Mock the environment variable for the API key and reload the module
        self.api_key_patcher = mock.patch.dict('os.environ', {'OPEN_WEATHER_BOT_API_KEY': 'fake_api_key'})
        self.api_key_patcher.start()
        reload(weather_bot)

        # Mock the requests.get() call to prevent real API calls
        self.requests_get_patcher = mock.patch('src.weather_bot.requests.get')
        self.mock_get = self.requests_get_patcher.start()
        # Set a default mock response (you can customize this in individual tests if needed)
        mock_response = mock.Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "main": {"temp": 70},
            "weather": [{"description": "clear sky"}]
        }
        self.mock_get.return_value = mock_response

    def tearDown(self):
        # Stop the patchers
        self.api_key_patcher.stop()
        self.requests_get_patcher.stop()

    @mock.patch('src.weather_bot.requests.get')
    def test_get_weather_success(self, mock_get):
        # Mock the response returned by requests.get
        mock_response = mock.Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "main": {"temp": 68.5},
            "weather": [{"description": "clear sky"}]
        }
        mock_get.return_value = mock_response

        city_name = "London"
        result = weather_bot.get_weather(city_name)

        # Checking against the new return format of the get_weather function
        expected_result = "In London, the current weather is: 68F with clear sky"
        self.assertEqual(result, expected_result)

    @mock.patch('src.weather_bot.requests.get')
    def test_get_weather_failure(self, mock_get):
        # Mock a failed response
        mock_response = mock.Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        city_name = "NonExistentCity"
        result = weather_bot.get_weather(city_name)

        expected_result = None
        self.assertEqual(result, expected_result)

    # Additional test to check unexpected response format
    @mock.patch('src.weather_bot.requests.get')
    def test_get_weather_unexpected_format(self, mock_get):
        # Mock an unexpected response format
        mock_response = mock.Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "unusual_key": "unusual_value"
        }
        mock_get.return_value = mock_response

        city_name = "London"
        result = weather_bot.get_weather(city_name)

        expected_result = None
        self.assertEqual(result, expected_result)

    @mock.patch('src.weather_bot.nlp')
    def test_low_similarity_statement(self, mock_nlp):
        # Mock the similarity computation
        mock_weather = mock.Mock()
        mock_statement = mock.Mock()
        mock_weather.similarity.return_value = 0.3  # Setting a low similarity score
        mock_nlp.side_effect = [mock_weather, mock_statement]

        # Provide a statement to the bot
        statement = "what is your name?"
        result = weather_bot.chatbot(statement)

        # Expected response when a statement has low similarity to typical weather questions
        expected_result = "I'm sorry, I can only provide information about the weather."

        self.assertEqual(result, expected_result)

    @mock.patch('src.weather_bot.nlp')
    def test_high_similarity_statement(self, mock_nlp):
        # Mock the NLP processing
        mock_weather = mock.Mock()
        mock_statement = mock.Mock()
        mock_ent = mock.Mock(label_="GPE", text="Brooklyn")
        mock_weather.similarity.return_value = 0.8
        mock_statement.ents = [mock_ent]  # Making the mock object iterable
        mock_nlp.side_effect = [mock_weather, mock_statement, mock_ent]

        # Provide a statement to the bot
        statement = "Is it hot in Brooklyn?"
        result = weather_bot.chatbot(statement)

        expected_result = "In Brooklyn, the current weather is: 70F with clear sky"
        self.assertEqual(result, expected_result)

    @mock.patch('src.weather_bot.nlp')
    def test_query_with_no_city_name(self, mock_nlp):
        mock_weather = mock.Mock()
        mock_statement = mock.Mock()
        mock_ent = mock.Mock(label_="GPE", text="")
        mock_weather.similarity.return_value = 0.8
        mock_statement.ents = []  # Making the mock object iterable
        mock_nlp.side_effect = [mock_weather, mock_statement]

        statement = "Tell me the weather?"
        result = weather_bot.chatbot(statement)

        expected_result = "You need to tell me a city to check."


    @mock.patch('src.weather_bot.get_weather')
    def test_valid_query(self, mock_get_weather):
        # Mocking the get_weather function to always return the same string
        mock_get_weather.return_value = "Mocked weather response"

        response = weather_bot.chatbot("Tell me the weather in Paris.")
        self.assertEqual(response, "Mocked weather response")


if __name__ == '__main__':
    main()
