from django.db import models

# Create your models here.
class GradesA(models.Model):
    uname = models.CharField(max_length=30)
    name = models.CharField(max_length=50)
    password = models.CharField(max_length=30)
    calc = models.FloatField()
    oop = models.FloatField()
    dld = models.FloatField()
    istd = models.FloatField()
    imgt = models.FloatField()
    ap = models.FloatField()

    def __str__(self):
        return self.name


class GradesB(models.Model):
    uname = models.CharField(max_length=30)
    name = models.CharField(max_length=50)
    password = models.CharField(max_length=30)
    calc = models.FloatField()
    oop = models.FloatField()
    dld = models.FloatField()
    istd = models.FloatField()
    imgt = models.FloatField()
    ap = models.FloatField()

    def __str__(self):
        return self.name

class GradesC(models.Model):
    uname = models.CharField(max_length=30)
    name = models.CharField(max_length=50)
    password = models.CharField(max_length=30)
    calc = models.FloatField()
    oop = models.FloatField()
    dld = models.FloatField()
    istd = models.FloatField()
    imgt = models.FloatField()
    ap = models.FloatField()

    def __str__(self):
        return self.name