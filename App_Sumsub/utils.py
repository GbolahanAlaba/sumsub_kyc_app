from django.shortcuts import render
from rest_framework.response import Response
import requests
from rest_framework import viewsets, status
from django.conf import settings
from functools import wraps
import hashlib
import hmac
import time




def handle_exceptions(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            error_message = str(e)
            return Response({"status": "failed", "message": error_message}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    return wrapper


@handle_exceptions
def sign_request(request: requests.Request) -> requests.PreparedRequest:
    prepared_request = request.prepare()
    now = int(time.time())
    method = request.method.upper()
    path_url = prepared_request.path_url  # includes encoded query params
    body = b'' if prepared_request.body is None else prepared_request.body
    if isinstance(body, str):
        body = body.encode('utf-8')

    data_to_sign = str(now).encode('utf-8') + method.encode('utf-8') + path_url.encode('utf-8') + body

    signature = hmac.new(
        settings.SUMSUB_SECRET_KEY.encode('utf-8'),
        data_to_sign,
        digestmod=hashlib.sha256
    )

    prepared_request.headers['X-App-Token'] = settings.SUMSUB_TOKEN
    prepared_request.headers['X-App-Access-Ts'] = str(now)
    prepared_request.headers['X-App-Access-Sig'] = signature.hexdigest()
    return prepared_request