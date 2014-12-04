from aristotle_mdr import models as MDR
from aristotle_mdr.views import render_if_user_can_view

def concept(*args,**kwargs):
    return render_if_user_can_view(MDR._concept,*args,**kwargs)

def objectclass(*args,**kwargs):
    return render_if_user_can_view(MDR.ObjectClass,*args,**kwargs)

def valuedomain(*args,**kwargs):
    return render_if_user_can_view(MDR.ValueDomain,*args,**kwargs)

def conceptualdomain(*args,**kwargs):
    return render_if_user_can_view(MDR.ConceptualDomain,*args,**kwargs)

def property(*args,**kwargs):
    return render_if_user_can_view(MDR.Property,*args,**kwargs)

def dataelementconcept(*args,**kwargs):
    return render_if_user_can_view(MDR.DataElementConcept,*args,**kwargs)

def dataelement(*args,**kwargs):
    return render_if_user_can_view(MDR.DataElement,*args,**kwargs)

def dataelementderivation(*args,**kwargs):
    return render_if_user_can_view(MDR.DataElementDerivation,*args,**kwargs)

def datatype(*args,**kwargs):
    return render_if_user_can_view(MDR.DataType,*args,**kwargs)

def unitofmeasure(*args,**kwargs):
    return render_if_user_can_view(MDR.UnitOfMeasure,*args,**kwargs)

def package(*args,**kwargs):
    return render_if_user_can_view(MDR.Package,*args,**kwargs)

def glossaryById(*args,**kwargs):
    return render_if_user_can_view(MDR.GlossaryItem,*args,**kwargs)
