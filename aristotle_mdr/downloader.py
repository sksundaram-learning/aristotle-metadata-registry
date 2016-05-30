from aristotle_mdr.utils import get_download_template_path_for_item
import cgi
import cStringIO as StringIO
from django.http import HttpResponse, Http404
# from django.shortcuts import render
from django.template.loader import select_template
from django.template import Context
from django.utils.safestring import mark_safe

import xhtml2pdf.pisa as pisa
import csv


def render_to_pdf(template_src, context_dict):
    # If the request template doesnt exist, we will give a default one.
    template = select_template([
        template_src,
        'aristotle_mdr/downloads/pdf/managedContent.html'
    ])
    context = Context(context_dict)
    html = template.render(context)
    result = StringIO.StringIO()
    pdf = pisa.pisaDocument(
        StringIO.StringIO(html.encode("UTF-8")),
        result,
        encoding='UTF-8'
    )
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return HttpResponse('We had some errors<pre>%s</pre>' % cgi.escape(html))


def download(request, downloadType, item):
    """Built in download method"""
    template = get_download_template_path_for_item(item, downloadType)
    from django.conf import settings
    page_size = getattr(settings, 'PDF_PAGE_SIZE', "A4")
    if downloadType == "pdf":
        subItems = item.get_download_items()
        return render_to_pdf(
            template,
            {
                'item': item,
                'subitems': subItems,
                'tableOfContents': len(subItems) > 0,
                'view': request.GET.get('view', '').lower(),
                'pagesize': request.GET.get('pagesize', page_size),
            }
        )

    elif downloadType == "csv-vd":
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="%s.csv"' % (
            item.name
        )

        writer = csv.writer(response)
        writer.writerow(['value', 'meaning', 'start date', 'end date', 'role'])
        for v in item.permissibleValues.all():
            writer.writerow(
                [v.value, v.meaning, v.start_date, v.end_date, "permissible"]
            )
        for v in item.supplementaryValues.all():
            writer.writerow(
                [v.value, v.meaning, v.start_date, v.end_date, "supplementary"]
            )

        return response


def bulk_download(request, downloadType, items, title=None, subtitle=None):
    """Built in download method"""
    template = 'aristotle_mdr/downloads/pdf/bulk_download.html'  # %(downloadType)
    from django.conf import settings
    page_size = getattr(settings, 'PDF_PAGE_SIZE', "A4")

    iids = {}
    item_querysets = {}  # {PythonClass:{help:ConceptHelp,qs:Queryset}}
    for item in items:
        print item
        if item and item.can_view(request.user):
            if item.__class__ not in iids.keys():
                iids[item.__class__] = []
            iids[item.__class__].append(item.pk)

            for metadata_type, qs in item.get_download_items():
                if metadata_type not in item_querysets.keys():
                    item_querysets[metadata_type] = {'help': None, 'qs': qs}
                else:
                    item_querysets[metadata_type]['qs'] &= qs

    help_topics = {}
    for metadata_type, ids_set in iids.items():
        query = metadata_type.objects.filter(pk__in=ids_set)
        if metadata_type not in item_querysets.keys():
            item_querysets[metadata_type] = {'help': None, 'qs': query}
        else:
            item_querysets[metadata_type]['qs'] &= query
        from aristotle_mdr.contrib.help.models import ConceptHelp

    for metadata_type in item_querysets.keys():
        item_querysets[metadata_type]['qs'] = item_querysets[metadata_type]['qs'].visible(request.user)
        item_querysets[metadata_type]['help'] = ConceptHelp.objects.filter(
            app_label=metadata_type._meta.app_label,
            concept_type=metadata_type._meta.model_name
        ).first()

    if title is None:
        if request.GET.get('title', None):
            title = request.GET.get('title')
        else:
            title = "Auto-generated document"

    if subtitle is None:
        if request.GET.get('subtitle', None):
            subtitle = request.GET.get('subtitle')
        else:
            _list = "<li>" + "</li><li>".join([item.name for item in items if item]) + "</li>"
            subtitle = mark_safe("Generated from the following metadata items:<ul>%s<ul>" % _list)

    if downloadType == "pdf":
        subItems = []

        return render_to_pdf(
            template,
            {
                'title': title,
                'subtitle': subtitle,
                'items': items,
                'included_items': sorted([(k, v) for k, v in item_querysets.items()], key=lambda (k, v): k._meta.model_name),
                'help_topics': help_topics,
                'pagesize': request.GET.get('pagesize', page_size),
            }
        )
