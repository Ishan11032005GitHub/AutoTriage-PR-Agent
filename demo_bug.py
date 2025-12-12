def get_username(user):
    if user.profile:
        return user.profile.name
    return None
