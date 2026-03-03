from django.apps import apps

StudentProfile = apps.get_model("accounts", "StudentProfile")
TeacherProfile = apps.get_model("accounts", "TeacherProfile")

def get_user_role(user_id, with_profile: bool = False):
    teacher = TeacherProfile.objects.filter(user_id=user_id).select_related().first()
    if teacher:
        return ("teacher", teacher) if with_profile else "teacher"

    student = StudentProfile.objects.filter(user_id=user_id).select_related().first()
    if student:
        return ("student", student) if with_profile else "student"

    return None