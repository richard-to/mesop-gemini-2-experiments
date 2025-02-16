# Copyright 2024 Google LLC
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

import mesop as me

from state.state import AppState
from components.page_scaffold import page_scaffold
from pages.home import home_content
from pages.audio_demo_v1 import audio_demo_content_v1
from pages.video_demo_v1 import video_demo_content_v1
from pages.tool_demo_v1 import tool_demo_content_v1


def on_load(e: me.LoadEvent):  # pylint: disable=unused-argument
  """On load event"""
  me.set_theme_mode("system")


@me.page(
  path="/",
  title="Mesop / Gemini Experiments",
  security_policy=me.SecurityPolicy(
    allowed_script_srcs=[
      "https://cdn.jsdelivr.net",
    ]
  ),
  on_load=on_load,
)
def home_demo():
  """Main Page"""
  state = me.state(AppState)
  with page_scaffold():  # pylint: disable=not-context-manager
    home_content(state)


@me.page(
  path="/audio_demo_v1",
  title="Audio Demo",
  security_policy=me.SecurityPolicy(
    allowed_script_srcs=[
      "https://cdn.jsdelivr.net",
    ]
  ),
  on_load=on_load,
)
def audio_demo_v1():
  """Main Page"""
  state = me.state(AppState)
  with page_scaffold():  # pylint: disable=not-context-manager
    audio_demo_content_v1(state)


@me.page(
  path="/video_demo_v1",
  title="Video Demo",
  security_policy=me.SecurityPolicy(
    allowed_script_srcs=[
      "https://cdn.jsdelivr.net",
    ]
  ),
  on_load=on_load,
)
def video_demo_v1():
  """Main Page"""
  state = me.state(AppState)
  with page_scaffold():  # pylint: disable=not-context-manager
    video_demo_content_v1(state)


@me.page(
  path="/tool_demo_v1",
  title="Tool Demo",
  security_policy=me.SecurityPolicy(
    allowed_script_srcs=[
      "https://cdn.jsdelivr.net",
    ]
  ),
  on_load=on_load,
)
def tool_demo_v1():
  """Main Page"""
  state = me.state(AppState)
  with page_scaffold():  # pylint: disable=not-context-manager
    tool_demo_content_v1(state)
