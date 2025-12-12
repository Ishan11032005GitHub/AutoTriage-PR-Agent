def get_username(user):
    return user.profile.name  # ❌ crashes if profile is None
