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

import base64
import os

from soar_sdk.SiemplifyDataModel import Attachment

ORIG_EMAIL_DESCRIPTION = "This is the original message as EML"
CASE_DETAILS_URL = "/external/v1/cases/GetCaseFullDetails/"


class AttachmentsManager:
    def __init__(self, siemplify):
        self.siemplify = siemplify
        self.logger = siemplify.LOGGER
        self.alert_entities = self.get_alert_entities()

    def get_alert_entities(self):
        return [
            entity for alert in self.siemplify.case.alerts for entity in alert.entities
        ]

    def get_attachments(self):
        response = self.siemplify.session.get(
            f"{self.siemplify.API_ROOT}{CASE_DETAILS_URL}"
            + self.siemplify.case.identifier,
        )
        wall_items = response.json()["wallData"]
        attachments = []
        for wall_item in wall_items:
            if wall_item["type"] == 4:
                if not wall_item["alertIdentifier"]:
                    attachments.append(wall_item)

        return attachments

    def get_alert_attachments(self):
        response = self.siemplify.session.get(
            f"{self.siemplify.API_ROOT}{CASE_DETAILS_URL}"
            + self.siemplify.case.identifier,
        )
        wall_items = response.json()["wallData"]
        attachments = []
        for wall_item in wall_items:
            if wall_item["type"] == 4:
                if (
                    self.siemplify.current_alert.identifier
                    == wall_item["alertIdentifier"]
                ):
                    attachments.append(wall_item)
        return attachments

    def add_attachment(
        self,
        filename,
        base64_blob,
        case_id,
        alert_identifier,
        description=None,
        is_favorite=False,
    ):
        """Add attachment
        :param file_path: {string} file path
        :param case_id: {string} case identifier
        :param alert_identifier: {string} alert identifier
        :param description: {string} attachment description
        :param is_favorite: {boolean} is attachment favorite
        :return: {dict} attachment_id
        """
        name, attachment_type = os.path.splitext(os.path.split(filename)[1])
        if not attachment_type:
            attachment_type = ".noext"
        attachment = Attachment(
            case_id,
            alert_identifier,
            base64_blob,
            attachment_type,
            name,
            description,
            is_favorite,
            len(base64.b64decode(base64_blob)),
            len(base64_blob),
        )
        attachment.case_identifier = case_id
        attachment.alert_identifier = alert_identifier
        address = (
            f"{self.siemplify.API_ROOT}/{'external/v1/sdk/AddAttachment?format=snake'}"
        )
        response = self.siemplify.session.post(address, json=attachment.__dict__)
        try:
            self.siemplify.validate_siemplify_error(response)
        except Exception as e:
            if "Attachment size" in e:
                raise Exception(
                    f"Attachment size should be < 5MB. Original file size: {attachment.orig_size}. Size after encoding: {attachment.size}.",
                )
        return response.json()
