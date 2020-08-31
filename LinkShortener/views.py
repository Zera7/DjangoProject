from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.core.validators import URLValidator
from django.db.models import F
from django.http import HttpResponseNotFound
from django.shortcuts import render, redirect

from LinkShortener import models


def home(request):
    """Main page

    :param request: an HttpRequest object that contains metadata about the request
    :return: reloads main page with data
    """
    url_error = ""  # Variable for the url error
    url_input = ""  # Variable to store the url input
    short_url = ""  # Variable to store a short url

    # Вызов view кнопкой "Shorten"
    if request.method == "POST":
        validator = URLValidator()
        try:
            url_input = request.POST.get("url", None)
            # Empty field
            if not url_input:
                url_error = "Empty field"
            else:
                validator(url_input)
        # Incorrect url
        except ValidationError as e:
            url_error = "Incorrect URL: " + str(e.message)
        except Exception as e:
            url_error = "Unexpected error: " + str(e)

        # Correct url
        if not url_error:
            link_db = models.Link()
            link_db.original = url_input
            link_db.hash = link_db.get_hash()
            link_db.save()
            short_url = request.build_absolute_uri(link_db.hash)

    return render(request, "home.html",
                  {"error": url_error, "shorturl": short_url})


def links(request):
    """All links page

    :param request: an HttpRequest object that contains metadata about the request
    :return: provides a template of all links with data
    """
    links = models.Link.objects.all().order_by('-redir_num')  # Get all links from database and order them by
    # num of redirects
    return render(request, "links.html",
                  {"links": links})


def delete(request, linkid):
    """Delete link method
    :param request: an HttpRequest object that contains metadata about the request
    :param linkid: an identifier of the link to delete
    :return: redirects to all links page
    """
    # Check if a link with such id exists
    try:
        link = models.Link.objects.get(id=linkid)
        link.delete()
    finally:
        return redirect("/links/")


def redir(request, linkhash):
    """Redirection method (from short link to original)
    :param request: an HttpRequest object that contains metadata about the request
    :param linkhash: a hash of the original link (the 6 chars after the domain name)
    :return: redirects to original link or drops an error 404 (Not found)
    """
    # Check if a link with such hash exists
    try:
        link = models.Link.objects.get(hash=linkhash)
        models.Link.objects.filter(hash=linkhash).update(redir_num=F('redir_num') + 1)
        return redirect(link.original)
    except ObjectDoesNotExist:
        return HttpResponseNotFound('<h1>Link not found.</h1>')
