from django.shortcuts import render

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import UserSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.parsers import MultiPartParser, FormParser
from .models import File
from .serializers import FileSerializer  # Create a serializer for File
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from django.views.decorators.csrf import csrf_exempt



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def protected_view(request):
    return Response({"message": "This is a protected view"})

class LoginView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)

        if user is not None:
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_200_OK)
        return Response({'detail': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)


class RegisterView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class FileUploadView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        file_obj = request.FILES['file']
        File.objects.create(user=request.user, file=file_obj)
        return Response({"message": "File uploaded successfully"}, status=status.HTTP_201_CREATED)
    
class ListFilesView(APIView):
    #curl -X GET http://127.0.0.1:8000/api/list-files/ \ -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzMwMTg2MDYxLCJpYXQiOjE3MzAxODU3NjEsImp0aSI6ImI0NWQ2ODJkNzZmOTRlY2I5MWM2N2MxN2RkMDY1YjExIiwidXNlcl9pZCI6MX0.41GiqdyZj_OJyRjAIibCtvyEEw994U35LC0dULKjQ9E"
    permission_classes = [IsAuthenticated]

    def get(self, request):
        files = File.objects.filter(user=request.user)
        serializer = FileSerializer(files, many=True)
        return Response(serializer.data)
    


class FileDownloadView(APIView):
    permission_classes = [IsAuthenticated]
    #test - curl -X GET http://127.0.0.1:8000/api/download/test1.rtf \ -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzMwMTg0NjQ1LCJpYXQiOjE3MzAxODQzNDUsImp0aSI6IjNiOTEyNTI2Y2I4YTQyOTFiOWE5M2MwMWQ5M2RhMWVkIiwidXNlcl9pZCI6MX0.IWBlEoJJ2NPt9mYyRcfq9pYQcP151VtjZJyQRX--JKM" -O


    def get(self, request, file_id):
        print("Attempting download")
        # Retrieve the file if it exists and belongs to the authenticated user
        file = get_object_or_404(File, id=file_id, user=request.user)
        # Create an HTTP response with the file data for download
        response = HttpResponse(file.file, content_type='application/octet-stream')
        response['Content-Disposition'] = f'attachment; filename="{file.file.name}"'
        print("Downloaded",file.file.name)
        return response

# @csrf_exempt
# class FileDeleteView(APIView):
#     permission_classes = [IsAuthenticated]

#     def delete(self, request, file_id):
#         # Retrieve the file if it exists and belongs to the authenticated user
#         file = get_object_or_404(File, id=file_id, user=request.user)
#         file.delete()
#         return Response({"message": "File deleted successfully"}, status=status.HTTP_204_NO_CONTENT)

class FileDeleteView(APIView):
    #test - curl -X DELETE -L  http://127.0.0.1:8000/api/delete/rig.rtf/ -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzMwMTg2NTAyLCJpYXQiOjE3MzAxODYyMDIsImp0aSI6ImU1NmMxZDZjM2QxZDRlOGViMjBlMjAwN2VjMmE3NWIxIiwidXNlcl9pZCI6MX0.PxklBJG33D4bwi_jnLmxUncAMUB5gA86cL_uMtb7egI"
    permission_classes = [IsAuthenticated]

    def delete(self, request, filename):
        try:
            file = File.objects.get(file='uploads/'+filename, user=request.user)  # Adjust according to your model
            file.delete()
            return Response({"message": "File deleted successfully"}, status=204)  # No content status
        except File.DoesNotExist:
            return Response({"detail": "File not found "+filename}, status=404)  # Not found status