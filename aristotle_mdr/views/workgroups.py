from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect

from aristotle_mdr import models as MDR
from aristotle_mdr import forms as MDRForms
from aristotle_mdr.views.utils import paginated_list
from aristotle_mdr.perms import user_in_workgroup, user_is_workgroup_manager

@login_required
def workgroup(request, iid):
    wg = get_object_or_404(MDR.Workgroup,pk=iid)
    if not user_in_workgroup(request.user,wg):
        raise PermissionDenied
    renderDict = {"item":wg,"workgroup":wg,"user_is_admin":user_is_workgroup_manager(request.user,wg)}
    renderDict['recent'] = MDR._concept.objects.filter(workgroup=iid).select_subclasses().order_by('-modified')[:5]
    page = render(request,wg.template,renderDict)
    return page

@login_required
def items(request, iid):
    wg = get_object_or_404(MDR.Workgroup,pk=iid)
    if not user_in_workgroup(request.user,wg):
        raise PermissionDenied
    items = MDR._concept.objects.filter(workgroup=iid).select_subclasses()
    context = {"item":wg,"workgroup":wg,"user_is_admin":user_is_workgroup_manager(request.user,wg)}
    return paginated_list(request,items,"aristotle_mdr/workgroupItems.html",context)

@login_required
def members(request, iid):
    wg = get_object_or_404(MDR.Workgroup,pk=iid)
    renderDict = {"item":wg,"workgroup":wg,"user_is_admin":user_is_workgroup_manager(request.user,wg)}
    if not user_in_workgroup(request.user,wg):
        raise PermissionDenied
    return render(request,"aristotle_mdr/workgroupMembers.html",renderDict)

def remove_role(request,iid,role,userid):
    workgroup = get_object_or_404(MDR.Workgroup,pk=iid)
    if not (workgroup and user_is_workgroup_manager(request.user,workgroup)):
        if request.user.is_anonymous():
            return redirect(reverse('django.contrib.auth.views.login')+'?next=%s' % request.path)
        else:
            raise PermissionDenied
    try:
        user = User.objects.get(id=userid)
        workgroup.removeRoleFromUser(role,user)
    except:
        pass
    return HttpResponseRedirect('/workgroup/%s/members'%(workgroup.id))

def add_members(request,iid):
    workgroup = get_object_or_404(MDR.Workgroup,pk=iid)
    if not (workgroup and user_is_workgroup_manager(request.user,workgroup)):
        if request.user.is_anonymous():
            return redirect(reverse('django.contrib.auth.views.login')+'?next=%s' % request.path)
        else:
            raise PermissionDenied
    if request.method == 'POST': # If the form has been submitted...
        form = MDRForms.AddWorkgroupMembers(request.POST) # A form bound to the POST data
        if form.is_valid():
            # process the data in form.cleaned_data as required
            users = form.cleaned_data['users']
            roles = form.cleaned_data['roles']
            for user in users:
                for role in roles:
                    workgroup.giveRoleToUser(role,user)
            return HttpResponseRedirect('/workgroup/%s/members'%(workgroup.id))
    else:
        form = MDRForms.AddWorkgroupMembers(initial={'roles':request.GET.getlist('role')})


    return render(request,"aristotle_mdr/actions/addWorkgroupMember.html",
            {"item":workgroup,
             "form":form,
             "role":request.GET.get('role')
                }
            )