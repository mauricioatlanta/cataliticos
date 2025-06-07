import requests

API_KEY = '27abd101e5bb2d9b1edd6691587b5aab'
url = 'https://api.metalpriceapi.com/v1/latest'

params = {
    'api_key': API_KEY,  # 👈 CORRECTO
    'base': 'USD',
    'symbols': 'XPT,XPD'  # Platino y Paladio
}

response = requests.get(url, params=params)
data = response.json()

print("✅ Respuesta API:")
print(data)
