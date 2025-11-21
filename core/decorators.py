from django.views.decorators.clickjacking import xframe_options_exempt

def allow_iframe(view):
    return xframe_options_exempt(view)
