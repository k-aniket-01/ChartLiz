from django.http import HttpResponse
from django.shortcuts import render,redirect
from .models import Portfolio
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
import requests
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from .models import Trade
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required   


def index(request):
    return render(request,"index.html")

@login_required
def market(request):
    return render(request,"market.html")

@login_required
def portfolio(request):
    return render(request,"portfolio.html")

def signup(request):
    if request.method == "POST":
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password == confirm_password:
            if User.objects.filter(username=username).exists():
                messages.error(request, "Username already exists!")
            elif User.objects.filter(email=email).exists():
                messages.error(request, "Email already registered!")
            else:
                user = User.objects.create_user(username=username, email=email, password=password)
                user.save()
                messages.success(request, "Account created successfully! You can log in now.")
                return redirect('login')
        else:
            messages.error(request, "Passwords do not match!")

    return render(request, 'signup.html')

def user_login(request):
    if request.method == "POST":
        username = request.POST.get('username')  # Use .get() to avoid key errors
        password = request.POST.get('password')

        if not username or not password:
            messages.error(request, "Please fill in all fields!")
            return render(request, 'login.html')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, "Login successful!")
            return redirect('dashboard')  # Redirect to your dashboard
        else:
            messages.error(request, "Invalid username or password!")

    return render(request, 'login.html')

def user_logout(request):
    logout(request)
    messages.success(request, "Logged out successfully!")
    return redirect('index')

@login_required
def dashboard(request):
    return render(request, 'dashboard.html')

def contact(request):
    return render(request, "contact.html")
def about(request):
    return render(request,'about.html')
@login_required
def learn(request):
    return render(request,'learn.html')


# views.py
import requests
from django.http import JsonResponse

def fetch_crypto_data(request):
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        'vs_currency': 'inr',
        'order': 'market_cap_desc',
        'per_page': 100,
        'page': 1,
        'sparkline': 'false'
    }
    response = requests.get(url, params=params)
    return JsonResponse(response.json(), safe=False)


def market(request, coin_id=None):
    return render(request, 'market.html', {'coin_id': coin_id})



def get_live_price(coin_id):
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd"
    response = requests.get(url)
    data = response.json()
    return data.get(coin_id, {}).get('usd')


@csrf_exempt
def save_prices(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            request.session['live_prices'] = data
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'invalid'})



from django.shortcuts import render
from .models import Portfolio


def get_current_price(symbol):
    # Mock data — you can later replace this with a real API call
    dummy_prices = {
        "BTC": 64000,
        "ETH": 3200,
        "DOGE": 0.12,
        "BNB": 550,
        "ADA": 0.45
    }
    return dummy_prices.get(symbol.upper(), 100) 


# def portfolio(request):
#     user = request.user
#     portfolio_items = Portfolio.objects.filter(user=user)

#     for item in portfolio_items:
#         current_price = get_current_price(item.symbol)
#         item.current_price = current_price
#         item.invested = item.total_quantity * item.average_price
#         item.value_now = item.total_quantity * current_price
#         item.profit = item.value_now - item.invested
#         item.percent_change = (item.profit / item.invested) * 100 if item.invested > 0 else 0
#         item.is_profit = item.profit >= 0

#     return render(request, 'portfolio.html', {
#         'username': user.username,
#         'portfolio_items': portfolio_items
#     })




@login_required
@login_required
def portfolio(request):
    portfolio_items = Portfolio.objects.filter(user=request.user)

    return render(request, 'portfolio.html', {
        'portfolio_items': portfolio_items,
        'user': request.user,
    })

# from django.shortcuts import render, redirect
# from django.contrib.auth.decorators import login_required
# import requests
# import json
# from .models import Trade  # Make sure Trade is properly imported

# @login_required
# def buy_view(request):
#     # Get the coin from the query parameters; default to bitcoin if not provided
#     coin = request.GET.get('coin', 'bitcoin').lower()
    
#     # Map the coin to its trading symbol (without prefix here for API use)
#     coin_symbol_map = {
#         'bitcoin': 'BTCUSDT',
#         'ethereum': 'ETHUSDT',
#         'solana': 'SOLUSDT',
#         'cardano': 'ADAUSDT',
#         'dogecoin': 'DOGEUSDT',
#         'ripple': 'XRPUSDT',
#         'polkadot': 'DOTUSDT',
#         'litecoin': 'LTCUSDT',
#         'avalanche': 'AVAXUSDT',
#         'chainlink': 'LINKUSDT',
#         'shiba': 'SHIBUSDT',
#         'tron': 'TRXUSDT',
#         'polygon': 'MATICUSDT',
#         'toncoin': 'TONUSDT'
#     }
    
#     symbol = coin_symbol_map.get(coin)
#     current_price = None
#     if symbol:
#         # Fetch real-time price from Binance
#         price_api = f'https://api.binance.com/api/v3/ticker/price?symbol={symbol}'
#         response = requests.get(price_api)
#         try:
#             current_price = float(response.json()['price'])
#         except (KeyError, ValueError):
#             current_price = 0.0

#     if request.method == 'POST':
#         # Get form data: quantity and desired price
#         quantity = float(request.POST.get('quantity'))
#         desired_price_input = request.POST.get('desired_price', '').strip()
#         # If the user does not specify a desired price, use the current price.
#         desired_price = float(desired_price_input) if desired_price_input else current_price
        
#         # Save the trade (update Trade model field names as needed)
#         Trade.objects.create(
#             user=request.user,
#             coin_name=coin,
#             symbol=symbol,
#             action='buy',
#             price=desired_price,  # Save the price at which the user wants to buy
#             quantity=quantity
#         )
        
#         return redirect('portfolio')  # Update URL name as needed

#     return render(request, 'buy.html', {
#         'coin_name': coin,
#         'symbol': symbol,
#         'current_price': current_price
#     })


from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
import requests
from .models import Buy, Portfolio, Trade

# @login_required
# def buy_view(request):
#     coin = request.GET.get('coin', 'bitcoin').lower()

#     coin_symbol_map = {
#         'bitcoin': 'BTCUSDT',
#         'ethereum': 'ETHUSDT',
#         'solana': 'SOLUSDT',
#         'cardano': 'ADAUSDT',
#         'dogecoin': 'DOGEUSDT',
#         'ripple': 'XRPUSDT',
#         'polkadot': 'DOTUSDT',
#         'litecoin': 'LTCUSDT',
#         'avalanche': 'AVAXUSDT',
#         'chainlink': 'LINKUSDT',
#         'shiba': 'SHIBUSDT',
#         'tron': 'TRXUSDT',
#         'polygon': 'MATICUSDT',
#         'toncoin': 'TONUSDT'
#     }

#     coin_symbol = coin_symbol_map.get(coin)
#     current_price = None

#     if coin_symbol:
#         price_api = f'https://api.binance.com/api/v3/ticker/price?symbol={coin_symbol}'
#         response = requests.get(price_api)
#         try:
#             current_price = float(response.json()['price'])
#         except:
#             current_price = 0.0

#     if request.method == 'POST':
#         quantity = float(request.POST.get('quantity'))
#         desired_price_input = request.POST.get('desired_price', '').strip()
#         desired_price = float(desired_price_input) if desired_price_input else current_price

#         # Save in Buy model
#         Buy.objects.create(
#             user=request.user,
#             coin_name=coin,
#             coin_symbol=coin_symbol,
#             price=desired_price,
#             quantity=quantity
#         )

#         # Save in Trade model
#         Trade.objects.create(
#             user=request.user,
#             coin_name=coin,
#             coin_symbol=coin_symbol,
#             action='buy',
#             price=desired_price,
#             quantity=quantity
#         )

#         # Update Portfolio
#         portfolio_entry, created = Portfolio.objects.get_or_create(
#             user=request.user,
#             coin_symbol=coin_symbol,
#             defaults={
#                 'coin_name': coin,
#                 'quantity': quantity,
#                 'buy_price': desired_price,
#                 'current_price': current_price
#             }
#         )

#         if not created:
#             total_cost = (portfolio_entry.quantity * portfolio_entry.buy_price) + (quantity * desired_price)
#             total_quantity = portfolio_entry.quantity + quantity
#             new_avg_price = total_cost / total_quantity

#             portfolio_entry.quantity = total_quantity
#             portfolio_entry.buy_price = new_avg_price
#             portfolio_entry.current_price = current_price
#             portfolio_entry.save()

#         return redirect('portfolio')

#     return render(request, 'buy.html', {
#         'coin_name': coin,
#         'coin_symbol': coin_symbol,
#         'current_price': current_price
#     })


from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Portfolio, Trade, Transaction
import requests

@login_required
def buy_view(request):
    coin = request.GET.get('coin', 'bitcoin').lower()
    coin_symbol_map = {
        'bitcoin': 'BTCUSDT',
        'ethereum': 'ETHUSDT',
        'solana': 'SOLUSDT',
        # Add more
    }

    symbol = coin_symbol_map.get(coin)
    current_price = 0.0

    if symbol:
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin}&vs_currencies=usd"
        response = requests.get(url)
        try:
            current_price = float(response.json()[coin]['usd'])
        except:
            current_price = 0.0

    if request.method == 'POST':
        quantity = float(request.POST.get('quantity'))
        desired_price_input = request.POST.get('desired_price', '').strip()
        desired_price = float(desired_price_input) if desired_price_input else current_price
        total_cost = quantity * desired_price

        wallet = Transaction.objects.get(user=request.user)
        if wallet.wallet_balance < total_cost:
            return render(request, 'buy.html', {
                'coin_name': coin,
                'symbol': symbol,
                'current_price': current_price,
                'error': 'Insufficient wallet balance!'
            })

        # Deduct wallet
        wallet.wallet_balance -= total_cost
        wallet.save()

        # Save to Trade
        Trade.objects.create(
            user=request.user,
            coin_name=coin,
            coin_symbol=symbol,
            quantity=quantity,
            price=desired_price,
            action='buy'
        )

        # Update Portfolio
        portfolio, created = Portfolio.objects.get_or_create(
            user=request.user, coin_symbol=symbol,
            defaults={'coin_name': coin, 'quantity': quantity, 'buy_price': desired_price}
        )
        if not created:
            total_quantity = portfolio.quantity + quantity
            new_avg_price = ((portfolio.quantity * portfolio.buy_price) + total_cost) / total_quantity
            portfolio.quantity = total_quantity
            portfolio.buy_price = new_avg_price

        portfolio.current_price = current_price
        portfolio.save()

        return redirect('portfolio')

    return render(request, 'buy.html', {
        'coin_name': coin,
        'symbol': symbol,
        'current_price': current_price
    })


from .models import Portfolio, Sell, Transaction
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone

@login_required
def sell_view(request):
    coin_symbol = request.GET.get('coin_symbol')
    coin_name = request.GET.get('coin_name')
    portfolio_id = request.GET.get('id')

    portfolio_item = get_object_or_404(Portfolio, id=portfolio_id, user=request.user)

    if request.method == 'POST':
        quantity_to_sell = float(request.POST.get('quantity'))
        current_price = float(request.POST.get('current_price'))

        if quantity_to_sell > portfolio_item.quantity:
            return render(request, 'sell.html', {
                'portfolio_item': portfolio_item,
                'error': 'You do not have enough coins to sell!',
                'current_price': current_price
            })

        # Update wallet
        wallet = get_object_or_404(Transaction, user=request.user)
        total_sale_value = quantity_to_sell * current_price
        wallet.wallet_balance += total_sale_value
        wallet.save()

        # Update portfolio
        portfolio_item.quantity -= quantity_to_sell
        if portfolio_item.quantity == 0:
            portfolio_item.delete()
        else:
            portfolio_item.save()

        # Save to Sell table
        Sell.objects.create(
            user=request.user,
            coin_name=coin_name,
            coin_symbol=coin_symbol,
            quantity=quantity_to_sell,
            sell_price=current_price,
            total_value=total_sale_value,
            timestamp=timezone.now()
        )

        return redirect('portfolio')

    # Get current price via JS — like buy.html
    return render(request, 'sell.html', {
        'portfolio_item': portfolio_item
    })


