# bookstore views
from django.http import HttpResponse
from django.utils.html import escape, linebreaks
from django.shortcuts import render_to_response

def storefront(request):
    return render_to_response("bookstore/storefront.html")
    
def readme(request):
    from os import path
    with open(path.join(path.dirname(path.realpath(__file__)), "README.md"), "rU") as f:
        text = f.read().decode("utf-8")

    try: import markdown
    except ImportError: html = linebreaks(escape(text))
    else: html = markdown.markdown(text)

    return render_to_response("bookstore/markdown.html", dict(content=html))