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

from rest_framework.fields import SerializerMethodField
from rest_framework.relations import HyperlinkedIdentityField, PrimaryKeyRelatedField
from rest_framework.serializers import ModelSerializer
from tests_description.api.v1.serializers import TestCaseSerializer
from tests_description.selectors.cases import TestCaseSelector
from tests_representation.models import Parameter, Test, TestPlan, TestResult
from tests_representation.selectors.parameters import ParameterSelector
from tests_representation.selectors.results import TestResultSelector


class ParameterSerializer(ModelSerializer):
    url = HyperlinkedIdentityField(view_name='api:v1:parameter-detail')

    class Meta:
        model = Parameter
        fields = ('id', 'project', 'data', 'group_name', 'url')


class TestPlanUpdateSerializer(ModelSerializer):
    test_cases = PrimaryKeyRelatedField(queryset=TestCaseSelector().case_list(), many=True, required=False)

    class Meta:
        model = TestPlan
        fields = (
            'id', 'name', 'parent', 'test_cases', 'started_at', 'due_date', 'finished_at', 'is_archive', 'project',
        )


class TestPlanInputSerializer(ModelSerializer):
    test_cases = PrimaryKeyRelatedField(queryset=TestCaseSelector().case_list(), many=True, required=False)
    parameters = PrimaryKeyRelatedField(queryset=ParameterSelector().parameter_list(), many=True, required=False)

    class Meta:
        model = TestPlan
        fields = (
            'id', 'name', 'parent', 'test_cases', 'parameters', 'started_at', 'due_date', 'finished_at', 'is_archive',
            'project',
        )


class TestSerializer(ModelSerializer):
    url = HyperlinkedIdentityField(view_name='api:v1:test-detail')

    class Meta:
        model = Test
        fields = ('id', 'project', 'case', 'plan', 'user', 'is_archive', 'created_at', 'updated_at', 'url')

        read_only_fields = ('project',)


class TestResultSerializer(ModelSerializer):
    url = HyperlinkedIdentityField(view_name='api:v1:testresult-detail')

    class Meta:
        model = TestResult
        fields = (
            'id', 'project', 'status', 'test', 'user', 'comment', 'is_archive', 'test_case_version', 'created_at',
            'updated_at', 'url'
        )

        read_only_fields = ('test_case_version', 'project', 'test')


class TestPlanTreeSerializer(ModelSerializer):
    children = SerializerMethodField()
    title = SerializerMethodField()

    class Meta:
        model = TestPlan
        fields = ('id', 'name', 'level', 'children', 'title')

    def get_title(self, instance):
        if instance.parameters is None:
            return instance.name
        parameters = ParameterSelector().parameter_name_list_by_ids(instance.parameters)
        return '{0} [{1}]'.format(instance.name, ', '.join(parameters))

    def get_children(self, value):
        return self.__class__(value.get_children(), many=True).data


class TestPlanTestResultSerializer(ModelSerializer):
    status = SerializerMethodField()
    updated_at = SerializerMethodField()

    class Meta:
        model = TestResult
        fields = (
            'id', 'status', 'comment', 'test_case_version', 'created_at', 'updated_at'
        )

    def get_status(self, instance):
        return instance.get_status_display()

    def get_updated_at(self, instance):
        return instance.updated_at.strftime("%d.%m.%Y %H:%M:%S")


class TestPlanTestSerializer(ModelSerializer):
    case = TestCaseSerializer()
    current_result = SerializerMethodField()
    test_results = TestPlanTestResultSerializer(many=True, read_only=True)

    def get_test_results(self, instance):
        return TestResultSelector().result_list_by_test_id(instance.id)

    class Meta:
        model = Test
        fields = ('id', 'case', 'plan', 'is_archive', 'created_at', 'updated_at', 'test_results',
                  'current_result')

    def get_current_result(self, instance):
        if instance.test_results.last():
            return instance.test_results.last().get_status_display()
        return None


class TestPlanOutputSerializer(ModelSerializer):
    url = HyperlinkedIdentityField(view_name='api:v1:testplan-detail')
    tests = TestPlanTestSerializer(many=True, read_only=True)
    title = SerializerMethodField()

    class Meta:
        model = TestPlan
        fields = (
            'id', 'name', 'parent', 'parameters', 'started_at', 'due_date', 'finished_at', 'is_archive',
            'tests', 'project', 'child_test_plans', 'url', 'title'
        )

    def get_title(self, instance):
        if instance.parameters is None:
            return instance.name
        parameters = ParameterSelector().parameter_name_list_by_ids(instance.parameters)
        return '{0} [{1}]'.format(instance.name, ', '.join(parameters))
