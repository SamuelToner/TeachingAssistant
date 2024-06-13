def user_is_teacher(request):
    is_teacher = False
    if request.user.is_authenticated:
        is_teacher = request.user.groups.filter(name="teacher").exists()
    return {"is_teacher": is_teacher}
