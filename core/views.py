from django.shortcuts import render, redirect
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.views.generic import TemplateView
from rembg import remove
from PIL import Image
import base64
import io


def home(request):
    if request.method == 'POST':
        img = request.FILES['image'].file
        img_rgb = Image.open(img).convert('RGBA')
        result = remove(img_rgb)
        transparent_image = Image.alpha_composite(Image.new("RGBA", result.size, (0, 0, 0, 0)), result)
        buffer = io.BytesIO()
        transparent_image.save(buffer, format='PNG')
        encoded_image = base64.b64encode(buffer.getvalue()).decode('utf-8')
        data_uri = f"data:image/png;base64,{encoded_image}"
        return render(request, 'removeBG.html', {'image': data_uri})
    else:
        return render(request, 'removeBG.html')


class ApiTemplate(TemplateView):
    template_name = 'api.html'


class ImageUploadView(APIView):    
    def post(self, request,format=None):
        img = request.FILES['image'].file
        img_rgb = Image.open(img).convert('RGBA')
        result = remove(img_rgb)
        transparent_image = Image.alpha_composite(Image.new("RGBA", result.size, (0, 0, 0, 0)), result)
        buffer = io.BytesIO()
        transparent_image.save(buffer, format='PNG')
        encoded_image = base64.b64encode(buffer.getvalue()).decode('utf-8')
        data_uri = f"data:image/png;base64,{encoded_image}"
        return Response({'image': data_uri})


class setBG(APIView):
    def post(self, request,format=None):
        imageURI = request.POST.get('imgData')
        color = request.POST.get('color')
        image_data = imageURI.split(",")[1]
        decoded_image_data = base64.b64decode(image_data)
        with open("image.png", "wb") as file:
            file.write(decoded_image_data)
        image = Image.open("image.png").convert('RGBA')
        image = remove(image)
        background = Image.new("RGB", image.size, color)
        result_image = Image.alpha_composite(background.convert("RGBA"), image.convert("RGBA"))
        buffer = io.BytesIO()
        result_image.save(buffer, format='PNG')
        encoded_image = base64.b64encode(buffer.getvalue()).decode('utf-8')
        data_uri = f"data:image/png;base64,{encoded_image}"
        return Response({'image': data_uri})
