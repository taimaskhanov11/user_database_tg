from tortoise import fields, models

__all__ = [
    [f"{sign}_HackedUser" for sign in list('abcdefghijklmnopqrstuvwxyz')]
]


class HackedUser(models.Model):
    email = fields.CharField(max_length=255, index=True)
    password = fields.CharField(max_length=255)
    service = fields.CharField(max_length=255)


def create_alphabet_tables():
    for sign in list('abcdefghijklmnopqrstuvwxyz'):
        class_name = f"{sign}_HackedUser"
        new_class = type(class_name, (models.Model,), {
            "email": fields.CharField(max_length=255, index=True),
            "password": fields.CharField(max_length=255),
            "service": fields.CharField(max_length=255),
        })
        globals()[class_name] = new_class
        # locals()[class_name] = new_class


create_alphabet_tables()
