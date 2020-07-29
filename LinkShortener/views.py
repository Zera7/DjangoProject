from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.shortcuts import render

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
