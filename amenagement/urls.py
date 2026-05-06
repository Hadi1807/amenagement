from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns = [
    path('', RedirectView.as_view(url='/login/', permanent=False)),
    path('admin/', admin.site.urls),
    path('', include('accounts.urls')),
    path('', include('core.urls')),
    path('facturation/', include('facturation.urls')),
    path('ia/', include('ia_chat.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)