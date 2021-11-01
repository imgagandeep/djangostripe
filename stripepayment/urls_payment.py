from django.urls import path
from  stripepayment.views import (
    all_products,
    HomeView,
    CreateCheckoutSessionView,
    SuccessView,
    CancelView,
    stripe_webhook
)


urlpatterns = [
    path('', all_products, name='product'),
    path('product_page/<pk>', HomeView.as_view(), name='product_page'),
    path('create-checkout-session/<pk>/', CreateCheckoutSessionView.as_view(), name='create-checkout-session'),
    path('success/', SuccessView.as_view(), name='success'),
    path('cancel/', CancelView.as_view(), name='cancel'),
    path('hooks/', stripe_webhook, name='stripe-webhook'),
]

