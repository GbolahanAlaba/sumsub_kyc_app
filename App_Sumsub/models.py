from django.db import models
import uuid


class VerificationStatus(models.Model):
    applicant_id = models.CharField(max_length=255, unique=True)
    country = models.CharField(max_length=255)
    id_doc_type = models.CharField(max_length=255)
    image_ids = models.JSONField()  # Store image IDs as a list
    image_review_results = models.JSONField(null=True, blank=True)  # Store review results as JSON
    forbidden = models.BooleanField(default=False)
    partial_completion = models.BooleanField(null=True, blank=True)
    step_statuses = models.JSONField(null=True, blank=True)  # Store step statuses as JSON
    image_statuses = models.JSONField(null=True, blank=True)  # Store image statuses as JSON
    selfie = models.JSONField(null=True, blank=True)  # Store selfie status, if applicable

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.applicant_id