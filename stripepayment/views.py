from django.shortcuts import redirect, render
from django.http import JsonResponse, HttpResponse
from django.core.mail import send_mail
from django.conf import settings
from django.views.generic.base import TemplateView
from django.views.decorators.csrf import csrf_exempt
from django.views import View
import stripe
from stripepayment.models import Product

stripe.api_key = settings.STRIPE_SECRET_KEY
YOUR_DOMAIN = settings.DOMAIN
# Create your views here.

def all_products(request):
    prods = Product.objects.all()
    context = {
        'prods': prods
    }
    return render(request, 'all_products.html', context)


class HomeView(TemplateView):
    template_name = 'product_page.html'

    def get_context_data(self, **kwargs):
        product_id = self.kwargs["pk"]
        prod_data = Product.objects.get(id=product_id)
        
        context = super(HomeView, self).get_context_data(**kwargs)
        context.update({
            'KEY': settings.STRIPE_PUBLIC_KEY,
            'all_products' : prod_data,
        })
        return context

class CreateCheckoutSessionView(View):
    def post(self, request, *args, **kwargs):
        product_id = self.kwargs["pk"]
        product = Product.objects.get(id = product_id)
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items = [{
                'price_data': {
                    'currency': 'inr',
                    'unit_amount': product.price * 100,
                    'product_data': {
                        'name': product.name,
                    },
                },
                'quantity': 1,
            }],
            metadata = {
                "product_id": product.id
            },
            mode = 'payment',
            success_url = YOUR_DOMAIN + '/success/',
            cancel_url = YOUR_DOMAIN + '/cancel/',
        )
        return JsonResponse({
            'id': checkout_session.id
        })


class SuccessView(TemplateView):
    template_name = 'success.html'


class CancelView(TemplateView):
    template_name = 'cancel.html'


@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    print(payload)
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)

    
    # Handle the checkout.session.completed event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        print(session)
        print(payload)

        customer_email = session['customer_details']['email']
        product_id = session['metadata']['product_id']

        product = Product.objects.get(id = product_id)

        send_mail(
            subject = "Here is your product",
            message = f"Thanks for your purchase",
            recipient_list = [customer_email],
            from_email = ""
        )
    
    return HttpResponse(status=200)



