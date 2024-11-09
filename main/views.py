from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.parsers import JSONParser
from paddleocr import PaddleOCR
import base64
import io
from PIL import Image
import re
import requests

from rest_framework import status
from .serializers.image_serializer import ImageSerializer

# Initialize PaddleOCR
ocr_model = PaddleOCR(use_angle_cls=True, lang='en')

@api_view(['POST'])
def identify(request):
    if request.method == 'POST':
        data = JSONParser().parse(request)
        image_data = data.get('image')

        if not image_data:
            print("Image Not Parsed")
            return JsonResponse({'error': 'No image provided'}, status=400)

        try:
            image_data = image_data.split(",")[1]
            image_bytes = base64.b64decode(image_data)
            image = Image.open(io.BytesIO(image_bytes))

            image_path = 'temp_image.jpg'
            image.save(image_path)

            print(f"Image saved at: {image_path}")

            ocr_results = ocr_model.ocr(image_path)

            print(f"OCR Results: {ocr_results}")

            if ocr_results is None:
                return JsonResponse({'error': 'OCR processing failed'}, status=500)

            formatted_results = []
            for line in ocr_results:
                for word_info in line:
                    formatted_results.append({
                        'text': re.sub(" ", "", word_info[1][0]),
                        'confidence': word_info[1][1],
                        'bounding_box': word_info[0]
                    })

            return JsonResponse({'results': formatted_results}, status=200)
        except Exception as e:
            print(f"Error: {e}")
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)

@api_view(['POST'])
def identify_direct(request):
    if request.method == 'POST':
        print("IS POST")
        image_data = None
        
        if 'image' in request.FILES:
            image_data = request.FILES['image'].read()
            image = Image.open(io.BytesIO(image_data))
        else:
            image_data = request.data.get('image')
            if image_data:
                image_data = image_data.split(",")[1]
                image_bytes = base64.b64decode(image_data)
                image = Image.open(io.BytesIO(image_bytes))

        if not image_data:
            print("Image Not Parsed")
            return JsonResponse({'error': 'No image provided'}, status=400)

        try:
            image_path = 'temp_image.jpg'
            image.save(image_path)

            print(f"Image saved at: {image_path}")

            ocr_results = ocr_model.ocr(image_path)

            print(f"OCR Results: {ocr_results}")

            if ocr_results is None:
                return JsonResponse({'error': 'OCR processing failed'}, status=500)

            formatted_results = []
            for line in ocr_results:
                for word_info in line:
                    formatted_results.append({
                        'text': re.sub(" ", "", word_info[1][0]),
                        'confidence': word_info[1][1],
                        'bounding_box': word_info[0]
                    })
            
            send_url = 'http://localhost:3000/api/trips'
            response = requests.post(send_url, json={'results': formatted_results})
            if response.status_code != 200:
                return JsonResponse({'error': 'Failed to send data to another endpoint'}, status=500)

            return JsonResponse({'results': formatted_results}, status=200)
        except Exception as e:
            print(f"Error: {e}")
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)


