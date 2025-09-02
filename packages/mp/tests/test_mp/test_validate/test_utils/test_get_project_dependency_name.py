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

from mp.validate.utils import get_project_dependency_name


def test_simple_equality_specifier() -> None:
    assert get_project_dependency_name("requests==2.25.1") == "requests"


def test_greater_than_or_equal_specifier() -> None:
    assert get_project_dependency_name("numpy>=1.20.0") == "numpy"


def test_less_than_specifier() -> None:
    assert get_project_dependency_name("pandas<2.0.0") == "pandas"


def test_no_specifier() -> None:
    assert get_project_dependency_name("django") == "django"


def test_with_hyphen_in_name() -> None:
    assert get_project_dependency_name("my-package>=1.0") == "my-package"


def test_with_underscore_in_name() -> None:
    assert get_project_dependency_name("my_package<1.2") == "my_package"


def test_with_extras_group() -> None:
    assert get_project_dependency_name("requests[security]==2.25.1") == "requests[security]"


def test_empty_string() -> None:
    assert get_project_dependency_name("") == ""


def test_string_starting_with_specifier() -> None:
    assert get_project_dependency_name(">=1.0") == ""
