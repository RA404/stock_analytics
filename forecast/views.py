from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse
from typing import IO
from decimal import Decimal

from .forms import LoadForm
from .models import StockData


def index(request: HttpRequest) -> HttpRequest:
    quote = StockData.objects.last()
    form = LoadForm(request.POST or None)
    context = {'form': form, 'quote': quote}
    template = 'stock/index.html'
    return render(request, template, context)


def load_data(request: HttpRequest) -> HttpResponse:
    form = LoadForm(request.POST, request.FILES or None)
    if form.is_valid():
        load_file_to_db(request.FILES['stock_data_file'])

    return redirect('stock:index')


def load_file_to_db(file: IO) -> None:
    with file as f:
        line = f.readline()
        while line:
            data_str = str(line.rstrip())
            data = data_str.strip('b\'').strip().split(';')
            date = data[2]
            StockData.objects.create(
                ticket=data[0],
                period=data[1],
                date='{0}-{1}-{2}'.format(date[:4], date[4:6], date[6:]),
                time=data[3],
                open=Decimal(data[4]),
                high=Decimal(data[5]),
                low=Decimal(data[6]),
                close=Decimal(data[7]),
                volume=Decimal(data[8])
            )
            line = f.readline()


def check_suggestion(request: HttpRequest, pk: int) -> HttpResponse:
    suggestion_list = [aim_to_average(), ]
    pnl = suggestion_list[int(pk)]
    fin_res = sum(pnl)
    count_of_quotes = StockData.objects.count()
    amount_of_deals = len(pnl)
    pnl.sort()
    unsuccessful_count = 0
    for i, deal in enumerate(pnl):
        if deal >= 0:
            unsuccessful_count = i + 1
            break
    successful_count = amount_of_deals - unsuccessful_count

    context = {
        'fin_res': fin_res,
        'count_of_quotes': count_of_quotes,
        'amount_of_deals': amount_of_deals,
        'unsuccessful_count': unsuccessful_count,
        'successful_count': successful_count,
    }
    template = 'stock/check_suggestion.html'
    return render(request, template, context)


def aim_to_average():
    values = get_default_values()
    pnl = []
    current_date = '0000-00-00'
    limit_free_candles = 60
    amount_free_candles = 0
    max_price = 0
    min_price = 0
    avg_price = 0

    start_date = '2021-04-25'
    end_date = '2022-07-08'
    quotes = StockData.objects.filter(
        ticket='MOEX.USDRUB_TMS:CETS',
        period='1',
        date__range=(start_date, end_date))
    amount_quotes = quotes.count()

    for i, quote in enumerate(quotes):
        # print(f'{i} date: {quote.date} open: {quote.open} high: {quote.high} low: {quote.low} close: {quote.close}')
        # print(values['price_buy'], values['price_sell'])

        amount_free_candles += 1

        if i == 0:
            current_date = quote.date
        elif i == amount_quotes-1:
            # close all
            deal_result = close_position(values, quote.close)
            if deal_result is not None:
                pnl.append(deal_result)
            # all parameters default
            values = get_default_values()
            amount_free_candles = 0
            # stop loop
            break
        elif current_date != quotes[i + 1].date:
            # close all
            deal_result = close_position(values, quote.close)
            if deal_result is not None:
                pnl.append(deal_result)
            # all parameters default
            values = get_default_values()
            amount_free_candles = 0
            # update current date
            current_date = quotes[i + 1].date
            # next loop iteration
            continue

        # if we have position check SL and TP
        if values['long_position']:
            deal_result = check_sl_and_tp(True, quote.low, quote.high, values)
            if deal_result is not None:
                pnl.append(deal_result)
                values = get_default_values()
        elif values['short_position']:
            deal_result = check_sl_and_tp(False, quote.low, quote.high, values)
            if deal_result is not None:
                pnl.append(deal_result)
                values = get_default_values()

        # check max and min
        # if changed then
        # free candle start from 0 and update max, min and recalculate avg
        if quote.high >= max_price or quote.low <= min_price:
            max_price = quote.high
            min_price = quote.low
            avg_price = (max_price + min_price) / 2
            if amount_free_candles > limit_free_candles:
                amount_free_candles = 0

        # check free candles
        if amount_free_candles < limit_free_candles:
            continue
        else:
            # do we have a position? if yes then continue
            if values['long_position'] or values['short_position']:
                continue
            else:
                # check should we open position
                good_price_for = find_price_for_trade(max_price,
                                                      min_price,
                                                      avg_price,
                                                      quote.low,
                                                      quote.high)
                if good_price_for['buy']:
                    values = {
                        'stop_loss': min_price,
                        'take_profit': avg_price,
                        'long_position': True,
                        'short_position': False,
                        'price_buy': good_price_for['price'],
                        'price_sell': 0,
                    }
                elif good_price_for['sell']:
                    values = {
                        'stop_loss': max_price,
                        'take_profit': avg_price,
                        'long_position': False,
                        'short_position': True,
                        'price_buy': 0,
                        'price_sell': good_price_for['price'],
                    }

    return pnl


def get_default_values():
    values = {
        'stop_loss': 0,
        'take_profit': 0,
        'long_position': False,
        'short_position': False,
        'price_buy': 0,
        'price_sell': 0,
    }
    return values


def close_deal(buy, sell):
    return sell - buy


def check_sl_and_tp(long, low, high, values):
    if long:
        # check SL first
        if low <= values['stop_loss']:
            return close_deal(
                buy=values['price_buy'],
                sell=values['stop_loss']
            )
        # check TP
        elif high >= values['take_profit']:
            return close_deal(
                buy=values['price_buy'],
                sell=values['take_profit']
            )
        else:
            return None
    else:
        # check SL first
        if high >= values['stop_loss']:
            return close_deal(
                buy=values['stop_loss'],
                sell=values['price_sell']
            )
        # check TP
        elif low <= values['take_profit']:
            return close_deal(
                buy=values['take_profit'],
                sell=values['price_sell']
            )
        else:
            return None


def find_price_for_trade(max_price, min_price, avg_price, low, high):
    good_price_for = {
        'sell': False,
        'buy': False,
        'price': 0.0,
    }
    sell_level = (max_price + avg_price) / 2
    buy_level = (min_price + avg_price) / 2

    if high > sell_level:
        good_price_for['sell'] = True
        good_price_for['price'] = sell_level
        return good_price_for
    elif low < buy_level:
        good_price_for['buy'] = True
        good_price_for['price'] = buy_level
        return good_price_for

    return good_price_for


def close_position(values, close):
    if values['long_position']:
        return close_deal(values['price_buy'], close)
    elif values['short_position']:
        return close_deal(close, values['price_sell'])
