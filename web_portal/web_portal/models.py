from django.db import models

class Molecule(models.Model):
    description = models.TextField(db_column="Description")
    numOfReads = models.IntegerField(db_column="# of reads (unnormalized)")
    sampleSource = models.TextField(db_column="Sample Name")

class UnknownMolecule(models.Model):
    levDistance = models.TextField(db_column="Levenshtein Distance Category")
    type = models.TextField(db_column="Type")
    numOfReads = models.IntegerField(db_column="# of reads (unnormalized)")
    sampleSource = models.TextField(db_column="Sample Name")

class SampleSource(models.Model):
    name = models.TextField(db_column="name")

    def __str__(self):
        return self.name