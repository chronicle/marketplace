"""Data models representing integration components.

This package defines a set of data classes that model various aspects of
an integration, such as test_actions, connectors, jobs, widgets, release notes,
custom families, mapping rules, and the integration itself. These data
models provide functionality to instantiate themselves from both the
"built" (final, deployable) and "non-built" (source) representations found
within the marketplace. They also offer methods to convert back and forth
between these formats, facilitating the build and deconstruction processes.
"""

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
