from core.models import Project
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import ArrayField
from django.core.validators import FileExtensionValidator, MinValueValidator
from django.db import models
from mptt.models import MPTTModel, TreeForeignKey
from rest_framework.exceptions import ValidationError
from tests_description.models import TestCase
from tests_representation.choices import TestStatuses
from users.models import User

from tms.models import BaseModel

UserModel = get_user_model()


class Parameter(BaseModel):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    data = models.TextField()
    group_name = models.CharField(max_length=settings.CHAR_FIELD_MAX_LEN)

    class Meta:
        default_related_name = 'parameters'
        unique_together = ('group_name', 'data',)


class TestPlan(MPTTModel, BaseModel):
    name = models.CharField(max_length=settings.CHAR_FIELD_MAX_LEN)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='child_test_planes')
    parameters = ArrayField(models.PositiveIntegerField(null=True, blank=True), null=True, blank=True)
    started_at = models.DateTimeField()
    due_date = models.DateTimeField()
    finished_at = models.DateTimeField(null=True, blank=True)
    is_archive = models.BooleanField(default=False)

    class Meta:
        default_related_name = 'test_plans'


class Test(BaseModel):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    case = models.ForeignKey(TestCase, on_delete=models.CASCADE)
    plan = models.ForeignKey(TestPlan, on_delete=models.CASCADE)
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE)
    is_archive = models.BooleanField(default=False)

    class Meta:
        default_related_name = 'tests'


class TestResult(BaseModel):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    status = models.IntegerField(choices=TestStatuses.choices, default=TestStatuses.UNTESTED)
    test = models.ForeignKey(Test, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    comment = models.TextField(blank=True)
    is_archive = models.BooleanField(default=False)
    test_case_version = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(settings.MIN_VALUE_POSITIVE_INTEGER)]
    )

    class Meta:
        default_related_name = 'test_results'


class Attachment(BaseModel):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    name = models.CharField(max_length=settings.CHAR_FIELD_MAX_LEN)
    filename = models.CharField(max_length=settings.CHAR_FIELD_MAX_LEN)
    content_type = models.CharField(max_length=settings.CHAR_FIELD_MAX_LEN)
    size = models.PositiveBigIntegerField()
    plan = models.ForeignKey(TestPlan, on_delete=models.CASCADE, null=True, blank=True)
    case = models.ForeignKey(TestCase, on_delete=models.CASCADE, null=True, blank=True)
    result = models.ForeignKey(TestResult, on_delete=models.CASCADE, null=True, blank=True)
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE)
    file = models.FileField(
        max_length=150,
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'txt', 'png', 'jpg', 'jpeg'])],
        upload_to='attachments'
    )

    def __str__(self):
        return str(self.file.url)

    def clean(self):
        if not self.result and not self.case and not self.plan:
            raise ValidationError({'detail': 'case, result or plan field should be specified'})

        parent_instances = [self.case, self.result, self.plan]
        projects = [parent_instance.project for parent_instance in parent_instances if parent_instance]
        if len(set(projects)) != 1:
            raise ValidationError({'detail': 'case, result, or plan have different project ids'})
