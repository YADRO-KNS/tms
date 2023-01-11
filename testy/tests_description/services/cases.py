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

from typing import Any, Dict

from core.services.attachments import AttachmentService
from tests_description.models import TestCase


class TestCaseService:
    non_side_effect_fields = ['name', 'project', 'suite', 'setup', 'scenario', 'teardown', 'estimate', 'description']

    def case_create(self, data: Dict[str, Any]) -> TestCase:
        case: TestCase = TestCase.model_create(
            fields=self.non_side_effect_fields,
            data=data,
        )

        for attachment in data.get('attachments', []):
            AttachmentService().attachment_set_content_object(attachment, case)

        return case

    def case_update(self, case: TestCase, data: Dict[str, Any]) -> TestCase:
        case, _ = case.model_update(
            fields=self.non_side_effect_fields,
            data=data,
        )

        AttachmentService().attachments_update_content_object(data.get('attachments', []), case)

        return case
