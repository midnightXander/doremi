import requests

def fetch_data(url, headers=None, params=None):
    """
    Fetch data from a REST API endpoint.

    Args:
        url (str): The API endpoint URL.
        headers (dict, optional): Headers to include in the request.
        params (dict, optional): Query parameters for the request.

    Returns:
        dict: The JSON response from the API or an error message.
    """
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()  # Raise an error for HTTP errors
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching API data: {e}")
        return {"error": str(e)}

print(fetch_data("https://api.jamendo.com/v3.0/tracks/?client_id=5ff3890d&format=jsonpretty&limit=10&include=musicinfo&groupby=artist_id"))
    