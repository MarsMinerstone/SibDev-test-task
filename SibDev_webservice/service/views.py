import csv
from rest_framework.views import APIView
from rest_framework.response import Response

from datetime import datetime
import pytz

from .models import Deal

from django.db.models import Sum, Count


class CSVMainView(APIView):
    def post(self, request, format=None):
        try:
            csv_file = request.FILES['file']
            decoded_file = csv_file.read().decode('utf-8').splitlines()
            reader = csv.DictReader(decoded_file)
            c = 0
            for row in reader:
                c += 1

                date_str = row['date']
                date_obj = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S.%f')
                timezone = pytz.timezone('Asia/Krasnoyarsk')
                date_obj = timezone.localize(date_obj)

                deal = Deal(
                    customer=row['customer'],
                    date=date_obj,
                    item=row['item'],
                    quantity=int(row['quantity']),
                    total=float(row['total'])
                )
                deal.save()
            return Response({'status': 'OK'})
        except Exception as e:
            return Response({'status': 'OK', "Desc": e})

    def delete(self, request, format=None):
        Deal.objects.all().delete()
        return Response({'message': 'All objects deleted successfully'})

    def get(self, request, format=None):
        top_customers = Deal.objects.values('customer').annotate(
            spent_money=Sum('total')
        ).order_by('-spent_money')[:5]
        top_customer_names = [customer['customer']
                              for customer in top_customers]

        top_customers_w_items = Deal.objects.values('customer', 'item').annotate(
            spent_money=Sum('total')
        ).filter(customer__in=top_customer_names)

        unique_customers = set(item['customer']
                               for item in top_customers_w_items)
        all_gems_of_customer = []
        for n_customer in unique_customers:
            items = [item['item']
                     for item in top_customers_w_items if item['customer'] == n_customer]
            all_gems_of_customer.append(
                {'customer': n_customer, 'items': list(set(items))})

        a_dict = {}
        for i in all_gems_of_customer:
            for j in i["items"]:
                if a_dict.get(j):
                    a_dict[j] += 1
                else:
                    a_dict[j] = 1

        popular_gems = [f for f in a_dict if a_dict[f] >= 2]

        gems = top_customers_w_items.filter(
            customer__in=[c['customer'] for c in top_customers]
        ).values('customer', 'item').annotate(
            item_count=Count('item')
        ).filter(item_count__gte=2).values_list('item', flat=True)

        response_data = []
        for customer in top_customers:
            customer_data = {
                'username': customer['customer'],
                'spent_money': customer['spent_money'],
                'gems': list(gems.filter(customer=customer['customer']).filter(item__in=popular_gems))
            }
            response_data.append(customer_data)

        return Response({'response': response_data})
