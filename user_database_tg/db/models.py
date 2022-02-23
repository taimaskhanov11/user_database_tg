import asyncio

from tortoise import fields, models


class HackedUser(models.Model):
    email = fields.CharField(max_length=255, index=True)
    password = fields.CharField(max_length=255)
    service = fields.CharField(max_length=255)


def create_alphabet_tables():
    for sign in list('ABCDEFGHIJKLMNOPQRSTUVWXYZ'):
        class_name = f"{sign}_User"
        new_class = type(class_name, (models.Model,), {
            "email": fields.CharField(max_length=255, index=True),
            "password": fields.CharField(max_length=255),
            "service": fields.CharField(max_length=255),
        })
        globals()[class_name] = new_class


