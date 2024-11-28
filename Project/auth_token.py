import requests

def obtain_auth_token():
    """Obtains an authentication token from the specified API."""
    api_url = "http://10.21.3.9:5001/v1/auth/Token/"
    api_key = '5678'
    headers = {'x-api-key': api_key}
    response = requests.get(api_url, headers=headers)
    
    if response.status_code == 200:
        token = response.json().get('token')
        if token:
            return token
        else:
            raise Exception("Token not found in response")
    else:
        raise Exception(f"Failed to obtain token: {response.status_code}, {response.text}")
