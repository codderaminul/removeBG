from django.apps import AppConfig
import os


class ShopifyAppConfig(AppConfig):
    name = 'shopify_apps'
    SHOPIFY_API_KEY= 'c7daa982332f3216feaa01e31e0cc359'
    SHOPIFY_API_SECRET= 'b0e4a11183a1a9a38d345d86ee576ee5'
    SHOPIFY_API_VERSION = '2023-04'
    SHOPIFY_API_SCOPE = ['read_products','read_orders','write_products']

