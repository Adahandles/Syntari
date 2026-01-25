import requests


class Net:
    def __init__(self):
        pass

    def make_request(self, url):
        response = requests.get(url)
        return response.status_code

    def post_data(self, url, data):
        response = requests.post(url, json=data)
        return response.status_code

    def put_data(self, url, data):
        response = requests.put(url, json=data)
        return response.status_code

    def delete_data(self, url):
        response = requests.delete(url)
        return response.status_code