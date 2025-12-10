from django.urls import path

from .views import QueryParseView

urlpatterns = [
    path("parse-query/", QueryParseView.as_view(), name="parse-query"),
]
