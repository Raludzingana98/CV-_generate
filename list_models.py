from google import genai
import os

API_KEY = "AIzaSyCIYuyLegEFkIhm5Vhb8s_SKUoIQTuV8xo"
client = genai.Client(api_key=API_KEY)

for model in client.models.list():
    print(model.name)
