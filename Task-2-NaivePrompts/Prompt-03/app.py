import os
import sys
from django.conf import settings
from django.core.management import execute_from_command_line
from django.http import HttpResponse
from django.shortcuts import render
from django.urls import path
from django.core.files.storage import FileSystemStorage

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

if not settings.configured:
    settings.configure(
        DEBUG=True,
        SECRET_KEY="a_very_secret_key_for_local_development",
        ROOT_URLCONF=__name__,
        TEMPLATES=[{
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'DIRS': [os.path.join(BASE_DIR, 'templates')],
        }],
        MEDIA_ROOT=os.path.join(BASE_DIR, 'media'),
        MEDIA_URL='/media/',
    )

# View 
def upload_view(request):
    uploaded_file_url = None
    
    if request.method == 'POST' and request.FILES.get('myfile'):
        myfile = request.FILES['myfile']
        fs = FileSystemStorage()
        filename = fs.save(myfile.name, myfile)
        uploaded_file_url = fs.url(filename)
        
    #  inline HTML template 
    html_content = """
             <!DOCTYPE html>
             <html>
             <head><title>Django File Upload</title></head>
             <body>
                 <h2>Upload a File to Disk</h2>
                 <form method="post" enctype="multipart/form-data">
                     {% csrf_token %}
                     <input type="file" name="myfile" required>
                     <button type="submit">Upload</button>
                 </form>
                 {% if uploaded_file_url %}
                     <p style="color: green;">Success!</p>
                     <p>File Link: <a href="{{ uploaded_file_url }}">{{ uploaded_file_url }}</a></p>
                 {% endif %}
             </body>
             </html>
    """
   
    from django.template import Template, Context
    t = Template(html_content)
    c = Context({'uploaded_file_url': uploaded_file_url, 'csrf_token': request.META.get('CSRF_COOKIE', '')})
    
   
    return HttpResponse(t.render(c))

#  URL Routing
from django.conf.urls.static import static

urlpatterns = [
    path('', upload_view, name='upload'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Execution
if __name__ == '__main__':
    execute_from_command_line(sys.argv)