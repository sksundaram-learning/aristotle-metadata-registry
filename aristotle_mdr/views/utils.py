from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render

paginate_sort_opts = {  "mod_asc":"modified",
                        "mod_desc":"-modified",
                        "name_asc":"name",
                        "name_desc":"-name",
                    }

@login_required
def paginated_list(request,items,template,extra_context={}):
    items = items.select_subclasses()
    sort_by=request.GET.get('sort',"mod_desc")
    if sort_by not in paginate_sort_opts.keys():
        sort_by="mod_desc"

    paginator = Paginator(
        items.order_by(paginate_sort_opts.get(sort_by)),
        request.GET.get('pp',20) # per page
        )

    page = request.GET.get('page')
    try:
        items = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        items = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        items = paginator.page(paginator.num_pages)
    context = {
        'sort':sort_by,
        'page':items,
        }
    context.update(extra_context)
    return render(request,template,context)

@login_required
def paginated_reversion_list(request,items,template,extra_context={}):
    sort_by=request.GET.get('sort',"mod_desc")
    if sort_by not in paginate_sort_opts.keys():
        sort_by="mod_desc"

    paginator = Paginator(
        items, #.order_by(paginate_sort_opts.get(sort_by)),
        request.GET.get('pp',20) # per page
        )

    page = request.GET.get('page')
    try:
        items = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        items = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        items = paginator.page(paginator.num_pages)
    context = {
        'sort':sort_by,
        'page':items,
        }
    context.update(extra_context)
    return render(request,template,context)
