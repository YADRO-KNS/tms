# TestY TMS - Test Management System
# Copyright (C) 2022 KNS Group LLC (YADRO)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Also add information on how to contact you by electronic and paper mail.
#
# If your software can interact with users remotely through a computer
# network, you should also make sure that it provides a way for users to
# get its source.  For example, if your program is a web application, its
# interface could display a "Source" link that leads users to an archive
# of the code.  There are many ways you could offer source, and different
# solutions will be better for different programs; see section 13 for the
# specific requirements.
#
# You should also get your employer (if you work as a programmer) or school,
# if any, to sign a "copyright disclaimer" for the program, if necessary.
# For more information on this, and how to apply and follow the GNU AGPL, see
# <http://www.gnu.org/licenses/>.
from functools import reduce

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.validators import FileExtensionValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.db.models import Q

from testy.models import BaseModel

__all__ = (
    'Project',
    'Attachment'
)
t = Q(app_label='core', model='Project')

UserModel = get_user_model()


class Project(BaseModel):
    name = models.CharField(_('name'), max_length=settings.CHAR_FIELD_MAX_LEN)
    description = models.TextField(_('description'), blank=True)

    class Meta:
        ordering = ('name',)
        verbose_name = _('project')
        verbose_name_plural = _('projects')

    def __str__(self) -> str:
        return self.name


class Attachment(BaseModel):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    name = models.CharField(max_length=settings.CHAR_FIELD_MAX_LEN)
    filename = models.CharField(max_length=settings.CHAR_FIELD_MAX_LEN)
    attachment_type = models.CharField(max_length=settings.CHAR_FIELD_MAX_LEN)
    size = models.PositiveBigIntegerField()

    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        # limit_choices_to={'model__in': ('Project',)}
    )

    object_id = models.PositiveIntegerField()

    content_object = GenericForeignKey('content_type', 'object_id')
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE)
    file = models.FileField(
        max_length=150,
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'txt', 'png', 'jpg', 'jpeg'])],
        upload_to='attachments'
    )

    def __str__(self):
        return str(self.file.url)

    # def clean(self):
    #     if not self.result and not self.case and not self.plan:
    #         raise ValidationError({'detail': 'case, result or plan field should be specified'})
    #
    #     parent_instances = [self.case, self.result, self.plan]
    #     projects = [parent_instance.project for parent_instance in parent_instances if parent_instance]
    #     if len(set(projects)) != 1:
    #         raise ValidationError({'detail': 'case, result, or plan have different project ids'})
