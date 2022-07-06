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
    suggestion_list = [around_average(), ]
    some_var = suggestion_list[int(pk)]
    context = {'some_var': some_var}
    template = 'stock/check_suggestion.html'
    return render(request, template, context)


def around_average():
    return 'hi'
