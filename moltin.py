import requests
from pprint import pprint
import os
from dotenv import load_dotenv


def get_access_token():
    load_dotenv()
    data = {
        'client_id': os.getenv('MOLTIN_CLIENT_ID'),
        'client_secret': os.getenv('MOLTIN_CLIENT_SECRET'),
        'grant_type': 'client_credentials'
    }
    url = 'https://api.moltin.com/oauth/access_token'
    response = requests.post(url, data=data)
    response.raise_for_status()
    access_token = response.json()['access_token']
    return access_token


def get_products():
    access_token = get_access_token()
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    url = 'https://api.moltin.com/v2/products'
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    products = response.json()['data']

    return products


def get_item_by_id(item_id):
    access_token = get_access_token()
    url = f'https://api.moltin.com/v2/products/{item_id}'
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()

    return response.json()['data']


def get_photo_url_by_id(photo_id):
    access_token = get_access_token()
    url = f'https://api.moltin.com/v2/files/{photo_id}'
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()

    return response.json()['data']['link']['href']


def add_product_to_cart(cart_id, product_id, product_amount):
    access_token = get_access_token()
    url = f'https://api.moltin.com/v2/carts/{cart_id}/items'
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
    }

    data = {
        "data": {
            "id": product_id,
            "type": "cart_item",
            "quantity": int(product_amount)}
    }
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()

    return response.json()


def get_cart_items(cart_id):
    access_token = get_access_token()
    headers = {
        'Authorization': f'Bearer {access_token}',
    }
    url = f'https://api.moltin.com/v2/carts/{cart_id}/items'
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    cart_items = response.json()['data']

    return cart_items


def delete_item_from_cart(cart_id, item_id):
    access_token = get_access_token()
    url = f'https://api.moltin.com/v2/carts/{cart_id}/items/{item_id}'
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    response = requests.delete(url, headers=headers)
    response.raise_for_status()

    return response.json()


def create_customer(first_name, last_name, email):
    access_token = get_access_token()
    url = 'https://api.moltin.com/v2/customers'
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    payload = {
        'data': {
            'name': f'{first_name} {last_name}',
            'type': 'customer',
            'email': email,
        }
    }
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()

    return response.json()['data']['id']
