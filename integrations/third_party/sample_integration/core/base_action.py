from __future__ import annotations

import os.path
from abc import ABC

from TIPCommon.base.action import Action

from .api_manager import ApiManager
from .auth_manager import AuthManager, build_auth_manager_params


class SampleAction(Action, ABC):
    """Base action class."""

    def _init_api_clients(self) -> ApiManager:
        """Prepare API client"""
        auth_manager_params = build_auth_manager_params(self.soar_action)
        auth_manager = AuthManager(auth_manager_params)

        return ApiManager(
            api_root=auth_manager.api_root,
            session=auth_manager.prepare_session(),
            logger=self.logger,
        )

    def save_temp_file(self, filename: str, content: str) -> str:
        """Saves content to file in temporary directory

        Args:
            filename (str): File name (Base name)
            content (str): File content

        Returns:
            str: Path to temporary file
        """
        temp_folder = self.soar_action.get_temp_folder_path()
        file_path = os.path.join(temp_folder, filename)
        with open(file_path, "w") as f:
            f.write(content)
        return file_path

    @property
    def result_value(self) -> bool:
        return self._result_value

    @result_value.setter
    def result_value(self, value: bool) -> None:
        self._result_value = value
