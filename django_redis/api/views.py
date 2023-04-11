import json, redis
from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

# creating redis instance to connect with redis-cli
REDIS_INSTANCE = redis.StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0)


@api_view(['GET', 'POST'])
def manage_items(request):
    """ function to manage multiple item from redis instance which perform action on redis memory """
    print("MANAGE ITEMS")
    if request.method == 'GET':
        items = {}
        count = 0
        for key in REDIS_INSTANCE.keys('*'):
            items[key.decode("utf-8")] = REDIS_INSTANCE.get(key)
            count += 1
        return Response({"count": count, "msg": f"found {count} items in redis", "items": items}, status=200)
    elif request.method == 'POST':
        item = json.loads(request.body)
        key = list(items.keys())[0] #NOTE: why
        value = item[key]
        # set value in redis
        REDIS_INSTANCE.set(key, value)
        return Response({"msg": f"set {key} to {value}"}, status=201)
    
@api_view(["GET", "PUT", "DELETE"])
def manage_item(request, *args, **kwargs):
    """ function to manage single item from redis instance which perform action on redis memory """
    print("MANAGE ITEM")
    if request.method == "GET":
        if kwargs['key']:
            value = REDIS_INSTANCE.get(kwargs["key"])
            if value:
                response = {
                    'key' : kwargs['key'],
                    'value': value,
                    'msg': 'success'
                }
                return Response(response, status=200)
            else:
                response = {
                    'key' : kwargs['key'],
                    'value': None,
                    'msg': 'Not Found'
                }
                return Response(response, status=404)
        else:
            response = {
                "msg" : "key not found in API"
            }
            return Response(response, status=200)
    elif request.method == "PUT":
        if kwargs["key"]:
            request_data = json.loads(request.body)
            new_value = request.data["new_value"]
            value = REDIS_INSTANCE.get(kwargs['key'])
            if value:
                # if value found in redis memory
                REDIS_INSTANCE.set(kwargs["key"], new_value)
                response = {
                    'key': kwargs['key'],
                    'value': value,
                    'msg': f"Successfully updated {kwargs['key']}"
                }
                return Response(response, status=200)
            else:
                # if value not found in redis memory
                response = {
                    'key': kwargs['key'],
                    'value': None,
                    'msg': 'Not found'
                }
                return Response(response, status=404)
    elif request.method == "DELETE":
        if kwargs["key"]:
            result = REDIS_INSTANCE.delete(kwargs["key"])
            if result in 1:
                # deleted key if found in redis memory
                response = {
                    'msg': f"{kwargs['key']} successfully deleted"
                }
                return Response(response, status=404)
            else:
                # if key not found
                response = {
                    'key': kwargs['key'],
                    'value': None,
                    'msg': 'Not found'
                }
                return Response(response, status=404)
            
