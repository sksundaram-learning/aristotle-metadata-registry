from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect
from django.shortcuts import render

from aristotle_mdr import forms as MDRForms
from aristotle_mdr import models as MDR
from aristotle_mdr.views.utils import paginated_list

@login_required
def home(request):
    page = render(request,"aristotle_mdr/user/userHome.html",{"item":request.user})
    return page

@login_required
def inbox(request,folder=None):
    if folder is None:
        # By default show only unread
        folder='unread'
    folder=folder.lower()
    if folder == 'unread':
        notices = request.user.notifications.unread().all()
    elif folder == "all" :
        notices = request.user.notifications.all()
    page = render(request,"aristotle_mdr/user/userInbox.html",
        {"item":request.user,"notifications":notices,'folder':folder})
    return page

@login_required
def admin_tools(request):
    if not request.user.is_superuser:
        raise PermissionDenied
    page = render(request,"aristotle_mdr/user/userAdminTools.html",{"item":request.user})
    return page

@login_required
def edit(request):
    if request.method == 'POST': # If the form has been submitted...
        form = MDRForms.UserSelfEditForm(request.POST) # A form bound to the POST data
        if form.is_valid():
            # process the data in form.cleaned_data as required
            request.user.first_name = form.cleaned_data['first_name']
            request.user.last_name = form.cleaned_data['last_name']
            request.user.email = form.cleaned_data['email']
            request.user.save()
            return HttpResponseRedirect('/account/home')
    else:
        form = MDRForms.UserSelfEditForm({
            'first_name':request.user.first_name,
            'last_name':request.user.last_name,
            'email':request.user.email,
            })
    return render(request,"aristotle_mdr/user/userEdit.html",{"form":form,})

@login_required
def favourites(request):
    items = request.user.profile.favourites.select_subclasses()
    context = { 'help':request.GET.get("help",False),
                'favourite':request.GET.get("favourite",False),}
    return paginated_list(request,items,"aristotle_mdr/user/userFavourites.html",context)

@login_required
def registrar_tools(request):
    if not request.user.profile.is_registrar:
        raise PermissionDenied
    page = render(request,"aristotle_mdr/user/userRegistrarTools.html")
    return page

@login_required
def review_list(request):
    if not request.user.profile.is_registrar:
        raise PermissionDenied
    if not request.user.is_superuser:
        ras = request.user.profile.registrarAuthorities
        wgs = MDR.Workgroup.objects.filter(registrationAuthorities__in=ras)
        items = MDR._concept.objects.filter(workgroup__in=wgs)
    else:
        items = MDR._concept.objects.all()
    items = items.filter(readyToReview=True,statuses=None)
    context={}
    return paginated_list(request,items,"aristotle_mdr/user/userReadyForReview.html",context)

@login_required
def workgroups(request):
    page = render(request,"aristotle_mdr/user/userWorkgroups.html")
    return page