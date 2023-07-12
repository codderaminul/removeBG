import datetime
from django.http import HttpResponse
from django.shortcuts import render,redirect
from shopify_apps.decorators import shop_login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import reverse
from django.template import RequestContext
from django.apps import apps
import hmac, base64, hashlib, binascii, os
from urllib.parse import parse_qs, urlparse
import shopify
from PIL import Image
from rembg import remove
import requests,io
import time
import threading



@shop_login_required
def index(request):
    try:
        products = shopify.Product.find(limit=70)
        orders = shopify.Order.find(limit=3, order="created_at DESC")
        
        return render(request, 'home/index.html', {'products': products, 'orders': orders})
    except:
        return redirect(logout)
    # for product in products:
    #     images = product.images
    #     if images:
    #         large_image_url = images[0].src
    #         print(large_image_url)
    # for product in products:
    #     if product.images:
    #         image = product.images[0]
    #         new_large_image_url = "https://www.w3schools.com/howto/img_snow.jpg"
    #         new_image = shopify.Image()
    #         new_image.src = new_large_image_url
    #         product.images = [new_image]
    #         product.save()
    #         print(new_image.src)


def _new_session(shop_url):
    api_version = apps.get_app_config('shopify_apps').SHOPIFY_API_VERSION
    return shopify.Session(shop_url, api_version) 

def authenticate(request):
    url = request.get_full_path()
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)
    shop_url = query_params.get('shop')[0] if 'shop' in query_params else 'kinefeli.myshopify.com'
    scope = apps.get_app_config('shopify_apps').SHOPIFY_API_SCOPE
    redirect_uri = request.build_absolute_uri(reverse(finalize))
    state = binascii.b2a_hex(os.urandom(15)).decode("utf-8")
    request.session['shopify_oauth_state_param'] = state
    permission_url = _new_session(shop_url).create_permission_url(scope, redirect_uri, state)

    print('shop_url=',shop_url)
    print('scope',scope)
    print('redirect_uri',redirect_uri)
    print('state',state)
    print('permission_url',permission_url)
    return redirect(permission_url)

    
def finalize(request):
    api_secret = apps.get_app_config('shopify_apps').SHOPIFY_API_SECRET
    params = request.GET.dict()
    print('params',params)
    if request.session['shopify_oauth_state_param'] != params['state']:
        messages.error(request, 'Anti-forgery state token does not match the initial request.')
        return redirect(reverse(authenticate))
    else:
        request.session.pop('shopify_oauth_state_param', None)

    myhmac = params.pop('hmac')
    line = '&'.join([
        '%s=%s' % (key, value)
        for key, value in sorted(params.items())
    ])
    h = hmac.new(api_secret.encode('utf-8'), line.encode('utf-8'), hashlib.sha256)
    if hmac.compare_digest(h.hexdigest(), myhmac) == False:
        messages.error(request, "Could not verify a secure login")
        return redirect(reverse(authenticate))

    try:
        shop_url = params['shop']
        session = _new_session(shop_url)
        request.session['shopify'] = {
            "shop_url": shop_url,
            "access_token": session.request_token(request.GET)
        }
    except Exception:
        messages.error(request, "Could not log in to Shopify store.")
        return redirect(reverse(authenticate))
    messages.info(request, "Logged in to shopify store.")
    request.session.pop('return_to', None)
    return redirect(request.session.get('return_to', reverse('index')))

def binary_search_products(products, target_id):
    left = 0
    right = len(products) - 1
    while left <= right:
        mid = (left + right) // 2
        mid_product = products[mid]
        if mid_product.id == target_id:
            return mid_product
        elif mid_product.id < target_id:
            left = mid + 1
        else:
            right = mid - 1
    return None

def removeBG(request, productId):
    products = shopify.Product.find(product_id=productId)
    sorted_products = sorted(products, key=lambda p: p.id)
    target_id = productId
    target_product = binary_search_products(sorted_products, target_id)
    for image in target_product.images:
        response = requests.get(image.src)
        with open("static/NewImage.jpg", "wb") as f:
            f.write(response.content)
        img_rgb=Image.open(os.path.join('static/NewImage.jpg'))
        result = remove(img_rgb)
        transparent_image = Image.alpha_composite(Image.new("RGBA", result.size, (0, 0, 0, 0)), result)
        buffer = io.BytesIO()
        transparent_image.save('static/NewImage.jpg', format='PNG')
        new_image = shopify.Image()
        with open('static/NewImage.jpg', 'rb') as f:
            encoded_image = base64.b64encode(f.read()).decode('utf-8')
        existing_image = image
        existing_image.attachment = encoded_image
        existing_image.save()
    return redirect('/')


# def removeBGoperation(image):
#     response = requests.get(image)
#     with open("static/NewImage.jpg", "wb") as f:
#         f.write(response.content)
#     img_rgb = Image.open('static/NewImage.jpg')
#     # Image processing operations...
#     result = remove(img_rgb)
#     transparent_image = Image.alpha_composite(Image.new("RGBA", result.size, (0, 0, 0, 0)), result)
#     buffer = io.BytesIO()
#     transparent_image.save(buffer, format='PNG')
#     buffer.seek(0)
#     return buffer.getvalue()

# def removeBG(request, productId):
#     products = shopify.Product.find(product_id=productId)
#     sorted_products = sorted(products, key=lambda p: p.id)
#     target_id = productId
#     target_product = binary_search_products(sorted_products, target_id)
#     if target_product:
#         image_count = len(target_product.images)
#         if image_count > 0:
#             start_time = time.time()  # Start measuring time
#             main_image_data = removeBGoperation(target_product.images[0].src)
#             target_product.images[0].attach_image(main_image_data, filename='main_image.png')
#             target_product.images[0].position = 1
#             target_product.images[0].save()
#             end_time = time.time()  # Stop measuring time
#             loading_time = end_time - start_time
#             print(f"Loading Time for First Image: {loading_time} seconds")
#         if image_count > 1:
#             threads = []
#             for i in range(1, image_count):
#                 thread = threading.Thread(target=process_image, args=(target_product, i))
#                 threads.append(thread)
#                 thread.start()
#             for thread in threads:
#                 thread.join()
#     return redirect('/')

# def process_image(product, index):
#     image_data = removeBGoperation(product.images[index].src)
#     image = shopify.Image()
#     image.attach_image(image_data, filename=f'image_{index}.png')
#     image.position = index + 1
#     product.images[index] = image  # Replace the original image with the modified image
#     image.save()


def logout(request):



    request.session.pop('shopify', None)
    messages.info(request, "Successfully logged out.")
    return redirect(reverse(authenticate))