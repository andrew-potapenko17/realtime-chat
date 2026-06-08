from django.db import models
import uuid
 
 
class TimestampedModel(models.Model):

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
 
    class Meta:
        abstract = True
        ordering = ["-created_at"]
 
 
class UUIDTimestampedModel(TimestampedModel):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
 
    class Meta(TimestampedModel.Meta):
        abstract = True
 