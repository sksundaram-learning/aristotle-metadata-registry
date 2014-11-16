from aristotle_mdr.views import render_if_user_can_view
import extension_test

def datasetspecification(*args,**kwargs):
    return render_if_user_can_view(extension_test.models.Question,*args,**kwargs)
