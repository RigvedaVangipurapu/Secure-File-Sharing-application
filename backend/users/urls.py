from django.urls import path
from .views import RegisterView, LoginView, protected_view, FileUploadView, ListFilesView, FileDownloadView, FileDeleteView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('protected/', protected_view, name='protected'),
    path('upload/', FileUploadView.as_view(), name='file-upload'),
    path('list-files/', ListFilesView.as_view(), name='list-files'),
    path('download/<str:filename>/', FileDownloadView.as_view(), name='download_file'),
    path('delete/<str:filename>/', FileDeleteView.as_view(), name='delete_file'),



]
