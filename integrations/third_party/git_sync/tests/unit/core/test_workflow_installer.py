# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import annotations

import sys
from unittest.mock import MagicMock, patch, Mock, PropertyMock, call


mock_modules = {
    'soar_sdk': Mock(),
    'soar_sdk.SiemplifyBase': Mock(),
    'soar_sdk.SiemplifyUtils': Mock(),
    'soar_sdk.SiemplifyAction': Mock(),
    'soar_sdk.SiemplifyJob': Mock(),
    'soar_sdk.SiemplifyConnector': Mock(),
    'SiemplifyAction': Mock(),
    'SiemplifyLogger': Mock(),
    'SiemplifyJob': Mock(),
    'SiemplifyConnector': Mock(),
    'SiemplifyConnectors': Mock(),
    'SiemplifyBase': Mock(),
    'SiemplifyUtils': Mock(),
    'SiemplifyDataModel': Mock(),
    'SiemplifyConnectorExecution': Mock(),
    'TIPCommon': Mock(),
    'TIPCommon.types': Mock(),
    'TIPCommon.rest': Mock(),
    'TIPCommon.rest.soar_api': Mock(),
    'TIPCommon.DataStream': Mock(),
    'TIPCommon.utils': Mock(),
}

for module_name, mock_module in mock_modules.items():
    sys.modules[module_name] = mock_module

sys.modules['TIPCommon.types'].SingleJson = Mock()
sys.modules['SiemplifyConnectors'].SiemplifyConnectorExecution = Mock()

import pytest  # noqa: E402
from ....core.GitSyncManager import WorkflowInstaller  # noqa: E402


class MockWorkflow:
    def __init__(self, workflow_data: dict):
        self.raw_data = workflow_data.copy()
        self.name = workflow_data.get("name", "test-workflow")
        self.identifier = workflow_data.get("identifier", "test-id")
        self.environments = workflow_data.get("environments", ["Default Environment"])
        self.modification_time = workflow_data.get("modificationTimeUnixTimeInMs", 0)
        if "stepsRelations" not in self.raw_data:
            self.raw_data["stepsRelations"] = []


@pytest.fixture
def workflow_installer(mock_api_client, mock_cache):
    mock_logger = MagicMock()
    mock_chronicle_soar = MagicMock()
    return WorkflowInstaller(mock_chronicle_soar, mock_api_client, mock_logger, mock_cache)


@pytest.fixture
def mock_workflow():
    return MockWorkflow({
        "identifier": "test-workflow-id",
        "name": "TestWorkflow",
        "environments": ["Default Environment"],
        "modificationTimeUnixTimeInMs": 1234567890,
        "steps": [{
            "identifier": "step-1",
            "instanceName": "Test_Step_1",
            "type": 0,
            "actionProvider": "Scripts",
            "integration": "TestIntegration",
            "parameters": [{"name": "IntegrationInstance", "value": "test-instance-id"}]
        }],
        "stepsRelations": [],
        "trigger": {"id": 0, "identifier": "trigger-id"}
    })


class TestWorkflowInstaller:

    def test_install_workflow_creates_new_when_not_exists(self, workflow_installer, mock_workflow):
        with patch.object(workflow_installer, '_workflow_exists', return_value=False), \
                patch.object(workflow_installer, 'install_new_workflow') as mock_install:
            workflow_installer.install_workflow(mock_workflow)
            mock_install.assert_called_once_with(mock_workflow)

    def test_install_workflow_updates_when_exists(self, workflow_installer, mock_workflow):
        with patch.object(workflow_installer, '_workflow_exists', return_value=True), \
                patch.object(workflow_installer, '_update_workflow_if_needed') as mock_update:
            workflow_installer.install_workflow(mock_workflow)
            mock_update.assert_called_once_with(mock_workflow)

    def test_workflow_exists_returns_correct_boolean(self, workflow_installer):
        installed_workflows = {"ExistingWorkflow": {"name": "ExistingWorkflow"}}
        with patch.object(type(workflow_installer), '_installed_playbooks',
                          new_callable=PropertyMock) as mock_prop:
            mock_prop.return_value = installed_workflows
            assert workflow_installer._workflow_exists("ExistingWorkflow") is True
            assert workflow_installer._workflow_exists("NonExistentWorkflow") is False

    def test_update_workflow_if_needed_skips_unmodified_workflow(
        self, workflow_installer, mock_workflow
    ):
        with (
            patch.object(workflow_installer, "_workflow_was_modified", return_value=False),
            patch.object(workflow_installer, "_filter_and_save_context") as mock_save,
            patch.object(workflow_installer, "update_local_workflow") as mock_update,
        ):
            workflow_installer._update_workflow_if_needed(mock_workflow)

            mock_save.assert_called_once()
            mock_update.assert_not_called()

    def test_update_workflow_if_needed_processes_modified_workflow(
        self, workflow_installer, mock_workflow
    ):
        with (
            patch.object(workflow_installer, "_workflow_was_modified", return_value=True),
            patch.object(workflow_installer, "_log_merge_conflicts") as mock_log_conflicts,
            patch.object(workflow_installer, "update_local_workflow") as mock_update,
        ):
            workflow_installer._update_workflow_if_needed(mock_workflow)

            mock_log_conflicts.assert_called_once()  # This could be added
            mock_update.assert_called_once_with(mock_workflow)

    def test_process_steps_handles_regular_action_step(self, workflow_installer, mock_workflow):
        with patch.object(workflow_installer, '_flatten_playbook_steps',
                          return_value=mock_workflow.raw_data["steps"]), \
                patch.object(workflow_installer,
                             '_assign_integration_instance_to_step') as mock_assign:
            workflow_installer._process_steps(mock_workflow)
            action_step = mock_workflow.raw_data["steps"][0]
            mock_assign.assert_called_once_with(action_step, mock_workflow.environments, None)

    def test_process_steps_handles_nested_block_step(self, workflow_installer):
        workflow_data = {
            "identifier": "test-id",
            "steps": [{"identifier": "block-step", "type": 5, "name": "TestBlock",
                       "parameters": []}],
            "stepsRelations": []
        }
        workflow = MockWorkflow(workflow_data)
        with patch.object(workflow_installer, '_flatten_playbook_steps',
                          return_value=workflow.raw_data["steps"]), \
                patch.object(workflow_installer, '_link_nested_block_step') as mock_link:
            workflow_installer._process_steps(workflow)
            block_step = workflow.raw_data["steps"][0]
            mock_link.assert_called_once_with(block_step)

    def test_assign_integration_instance_copies_from_existing_step(self, workflow_installer):
        step = {
            "type": 0,
            "actionProvider": "Scripts",
            "integration": "TestIntegration",
            "parameters": [{"name": "IntegrationInstance", "value": ""}],
        }
        existing_step = {
            "parameters": [
                {"name": "IntegrationInstance", "value": "existing-instance"},
                {"name": "FallbackIntegrationInstance", "value": "fallback-instance"},
            ]
        }
        environments = ["Test Environment"]

        with (
            patch.object(workflow_installer, "_get_step_parameter_by_name") as mock_get,
            patch.object(workflow_installer, "_set_step_parameter_by_name") as mock_set,
        ):
            mock_get.side_effect = [{"value": "existing-instance"}, {"value": "fallback-instance"}]

            workflow_installer._assign_integration_instance_to_step(
                step, environments, existing_step
            )

            expected_calls = [
                call(step, "IntegrationInstance", "existing-instance"),
                call(step, "FallbackIntegrationInstance", "fallback-instance"),
            ]

            mock_set.assert_has_calls(expected_calls, any_order=True)
            assert mock_set.call_count == len(expected_calls)

    def test_process_steps_handles_loop_step_identifier_mapping(self, workflow_installer):
        workflow_data = {
            "identifier": "test-workflow-id",
            "steps": [
                {"identifier": "old-step-1", "instanceName": "Regular_Step", "type": 0,
                 "actionProvider": "Scripts", "integration": "TestIntegration", "parameters": []},
                {"identifier": "old-loop-step", "instanceName": "Loop_Step", "type": 2,
                 "startLoopStepIdentifier": "old-step-1", "endLoopStepIdentifier": "old-step-2"},
                {"identifier": "old-step-2", "instanceName": "End_Step", "type": 0,
                 "actionProvider": "Scripts", "integration": "TestIntegration", "parameters": []}
            ],
            "stepsRelations": []
        }
        workflow = MockWorkflow(workflow_data)
        existing_workflow = {
            "steps": [
                {"identifier": "new-step-1", "originalStepIdentifier": "new-step-1",
                 "instanceName": "Regular_Step", "parameters": []},
                {"identifier": "new-loop-step", "originalStepIdentifier": "new-loop-step",
                 "instanceName": "Loop_Step", "parameters": []},
                {"identifier": "new-step-2", "originalStepIdentifier": "new-step-2",
                 "instanceName": "End_Step", "parameters": []}
            ]
        }
        with patch.object(workflow_installer, '_assign_integration_instance_to_step'), \
                patch.object(workflow_installer, '_link_nested_block_step'):
            workflow_installer._process_steps(workflow, existing_workflow)

            # Check that step identifiers were updated in the workflow steps
            steps = workflow.raw_data["steps"]
            assert steps[0]["identifier"] == "new-step-1"  # Regular step
            assert steps[1]["identifier"] == "new-loop-step"  # Loop step
            assert steps[2]["identifier"] == "new-step-2"  # End step

            # Check that loop step identifiers were updated
            loop_step = steps[1]
            assert loop_step["startLoopStepIdentifier"] == "new-step-1"
            assert loop_step["endLoopStepIdentifier"] == "new-step-2"
