import time
from datetime import datetime

from core.api.v1.serializers import ProjectSerializer
from core.models import Project
from core.services.projects import ProjectService
from dateutil.relativedelta import relativedelta
from testrail_migrator.serializers import ParameterSerializer, TestSerializer
from tests_description.api.v1.serializers import TestCaseSerializer, TestSuiteSerializer
from tests_description.services.cases import TestCaseService
from tests_description.services.suites import TestSuiteService
from tests_representation.api.v1.serializers import TestPlanInputSerializer, TestResultSerializer
from tests_representation.services.parameters import ParameterService
from tests_representation.services.results import TestResultService
from tests_representation.services.testplans import TestPlanService
from tests_representation.services.tests import TestService


class TestyCreator:
    @staticmethod
    def create_suites(suites, project_id):
        suite_data_list = []
        src_ids = []
        for suite in suites:
            src_ids.append(suite['id'])
            suite_data_list.append({'name': suite['name'], 'project': project_id, })
        serializer = TestSuiteSerializer(data=suite_data_list, many=True)
        serializer.is_valid(raise_exception=True)
        created_suites = TestSuiteService().suites_bulk_create(serializer.validated_data)

        return dict(zip(src_ids, [created_suite.id for created_suite in created_suites]))

    @staticmethod
    def create_cases(cases, suite_mappings, project_id):
        cases_data_list = []
        src_case_ids = []
        for case in cases:
            src_case_ids.append(case['id'])
            case_data = {
                'name': case['title'],
                'project': project_id,
                'suite': suite_mappings.get(case['suite_id']),
                'scenario': case['custom_steps'],
            }
            cases_data_list.append(case_data)
        serializer = TestCaseSerializer(data=cases_data_list, many=True)
        serializer.is_valid(raise_exception=True)
        created_cases = TestCaseService().cases_bulk_create(serializer.validated_data)
        return dict(zip(src_case_ids, [created_case.id for created_case in created_cases]))

    @staticmethod
    def create_configs(config_groups, project_id):
        parameters_mappings = {}
        parameter_data_list = []
        src_config_ids = []
        for config_group in config_groups:
            for config in config_group['configs']:
                src_config_ids.append(config['id'])
                parameter_data = {
                    'group_name': config_group['name'],
                    'data': config['name'],
                    'project': project_id,
                }
                parameter_data_list.append(parameter_data)

        serializer = ParameterSerializer(data=parameter_data_list, many=True)
        serializer.is_valid(raise_exception=True)
        created_parameters = ParameterService().parameter_bulk_create(serializer.validated_data)
        for tr_config_id, testy_parameter in zip(src_config_ids, created_parameters):
            parameters_mappings.update({tr_config_id: testy_parameter.id})

        return parameters_mappings

    @staticmethod
    def create_milestones(milestones, project_id):
        milestones_mapping = {}
        parent_milestones = []
        for milestone in milestones:
            milestone_data = {
                'project': project_id,
                'name': milestone['name'],
                'is_archive': milestone['is_completed'],
                'started_at': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(milestone['started_on'])),
                'finished_at': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(milestone['completed_on'])),
                'due_date': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(milestone['due_on']))
            }
            parent_milestones.append(milestone_data)

        serializer = TestPlanInputSerializer(data=parent_milestones, many=True)
        serializer.is_valid(raise_exception=True)
        test_plans = TestPlanService().testplan_bulk_create(serializer.validated_data)
        for tr_milestone, testy_milestone in zip(milestones, test_plans):
            milestones_mapping.update({tr_milestone['id']: testy_milestone.id})

        for milestone in milestones:
            if not milestone['milestones']:
                continue
            child_milestones_data_list = []
            for child_milestone in milestone['milestones']:
                milestone_data = {
                    'project': project_id,
                    'name': child_milestone['name'],
                    'is_archive': child_milestone['is_completed'],
                    'started_at': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(milestone['started_on'])),
                    'finished_at': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(child_milestone['completed_on'])),
                    'due_date': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(child_milestone['due_on'])),
                    'parent': milestones_mapping[milestone['id']]
                }
                child_milestones_data_list.append(milestone_data)

            serializer = TestPlanInputSerializer(data=child_milestones_data_list, many=True)
            serializer.is_valid(raise_exception=True)
            test_plans = TestPlanService().testplan_bulk_create(serializer.validated_data)

            for tr_milestone, testy_milestone in zip(milestone['milestones'], test_plans):
                milestones_mapping.update({tr_milestone['id']: testy_milestone.id})

        return milestones_mapping

    @staticmethod
    def create_plans(plans, milestones_mappings, project_id, skip_root_plans: bool = True):
        plan_data_list = []
        plan_mappings = {}
        for plan in plans:
            mapping_id = plan['milestone_id']
            due_date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(plan.get('due_on')))
            if not plan.get('due_on'):
                due_date = (datetime.now() + relativedelta(years=5, days=5)).strftime('%Y-%m-%d %H:%M:%S')
            plan_data = {
                'project': project_id,
                'name': plan['name'],
                'is_archive': plan['is_completed'],
                'started_at': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(plan['created_on'])),
                'finished_at': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(plan['completed_on'])),
                'due_date': due_date,
            }
            if not mapping_id and skip_root_plans:
                continue
            if mapping_id:
                plan_data['parent'] = milestones_mappings[mapping_id]
            plan_data_list.append(plan_data)

        serializer = TestPlanInputSerializer(data=plan_data_list, many=True)
        serializer.is_valid(raise_exception=True)
        test_plans = TestPlanService().testplan_bulk_create(serializer.validated_data)
        for tr_milestone, testy_milestone in zip(plans, test_plans):
            plan_mappings.update({tr_milestone['id']: testy_milestone.id})

        return plan_mappings

    @staticmethod
    def create_runs_parent_plan(runs, plan_mappings, config_mappings, tests, case_mappings, project_id):
        run_data_list = []
        src_tests = []
        for idx, run in enumerate(runs, start=1):
            parent = plan_mappings.get(run['plan_id'])
            if not parent:
                continue
            tests_for_run = [test for test in tests if test['run_id'] == run['id']]
            src_tests.extend(tests_for_run)
            cases = [case_mappings[test['case_id']] for test in tests_for_run]
            parameters = [config_mappings[config_id] for config_id in run['config_ids']]
            due_date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(run.get('due_on')))
            if not run.get('due_on'):
                due_date = (datetime.now() + relativedelta(years=5, days=5)).strftime('%Y-%m-%d %H:%M:%S')
            run_data = {
                'project': project_id,
                'name': run['name'],
                'started_at': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(run['created_on'])),
                'due_date': due_date,
                'parent': parent,
                'test_cases': cases,
                'parameters': parameters
            }
            run_data_list.append(run_data)
        serializer = TestPlanInputSerializer(data=run_data_list, many=True)
        serializer.is_valid(raise_exception=True)
        created_tests = TestPlanService().testplan_bulk_create_with_tests(serializer.validated_data)
        return dict(zip(
            [src_test['id'] for src_test in src_tests],
            [created_test.id for created_test in created_tests])
        )

    @staticmethod
    def create_project(project) -> Project:
        data = {
            'name': project['name'],
            'description': project['announcement'] if project['announcement'] else ''
        }
        serializer = ProjectSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        return ProjectService().project_create(serializer.validated_data)

    @staticmethod
    def create_tests(tests, case_mappings, plans_mappings, project_id):
        test_data_list = []
        tests_mappings = {}
        for test in tests:
            if not case_mappings.get(test['case_id']) or not plans_mappings.get(test['run_id']):
                continue
            test_data = {
                'project': project_id,
                'case': case_mappings[test['case_id']],
                'plan': plans_mappings[test['run_id']]
            }
            test_data_list.append(test_data)
        serializer = TestSerializer(data=test_data_list, many=True)
        serializer.is_valid(raise_exception=True)
        created_tests = TestService().tests_bulk_create_by_data_list(serializer.validated_data)
        for tr_test, testy_test in zip(tests, created_tests):
            tests_mappings.update({tr_test['id']: testy_test.id})

        return tests_mappings

    @staticmethod
    def create_results(results, tests_mappings, user):
        statuses = {
            1: 1,  # passed
            5: 0,  # failed
            8: 2,  # skipped
            2: 4,  # Retest
            3: 5,  # Untested
            4: 3  # Not matching retest in tr / broken in testy
        }
        created_results = []
        for idx, result in enumerate(results):
            print(f'Processing result {idx} of {len(results)}')
            if not tests_mappings.get(result['test_id']):
                continue
            result_data = {
                'status': statuses.get(result['status_id'], 5),
                'comment': result['comment'],
                'test': tests_mappings[result['test_id']],
            }
            serializer = TestResultSerializer(data=result_data)
            serializer.is_valid(raise_exception=True)
            created_results.append(TestResultService().result_create(serializer.validated_data, user))
        return created_results
