"""Abstract base models for the project."""

from django.db import models


class TimeStampedModel(models.Model):
    """Abstract model providing created_at and updated_at timestamps."""

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
