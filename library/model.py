import uuid

from django.db import models
from django.db.models.fields.related import ForeignObjectRel, RelatedField
from django.utils import timezone


class DictUpdateMixin:
    def is_simple_editable_field(self, field):
        return (
            field.editable
            and not field.primary_key
            and not isinstance(field, (ForeignObjectRel, RelatedField))
        )

    def update_from_dict(self, attrs, excluded_field_names=[], commit=True):
        """
        Update method for Django model
        :param attrs: The dict containing the field and values to be updaed
        :param excluded_field_names: A list of field names to exclude from being updates
        :param commit: Boolean. Do you want to save the values?
        :return: void
        """
        allowed_field_names = [
            f.name for f in self._meta.get_fields() if self.is_simple_editable_field(f)
        ]

        set1 = set(allowed_field_names)
        set2 = set(excluded_field_names)
        allowed_field_names = list(set1 - set2)

        for attr, val in attrs.items():
            if attr in allowed_field_names:
                setattr(self, attr, val)


class BaseModelManager(models.Manager):
    def get_queryset(self):
        return (
            super(BaseModelManager, self)
            .get_queryset()
            .filter(archived__isnull=True)
            .filter(archived=None)
        )


class BaseModel(models.Model, DictUpdateMixin):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    archived = models.DateTimeField(blank=True, null=True, editable=False)
    last_modified = models.DateTimeField(auto_now=True)
    date_created = models.DateTimeField(auto_now_add=True)

    objects = BaseModelManager()
    super_objects = models.Manager()

    def archive(self, using=None, keep_parents=False):
        import datetime

        self.archived = timezone.now()
        super(BaseModel, self).save(using=using)

    class Meta:
        abstract = True
        ordering = ["-last_modified"]
