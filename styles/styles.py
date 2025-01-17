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


SIDENAV_MIN_WIDTH=68
SIDENAV_MAX_WIDTH=200

DEFAULT_MENU_STYLE = me.Style(align_content="left")

_FANCY_TEXT_GRADIENT = me.Style(
    color="transparent",
    background=(
        "linear-gradient(72.83deg,#4285f4 11.63%,#9b72cb 40.43%,#d96570 68.07%)"
        " text"
    ),
)

MAIN_COLUMN_STYLE = me.Style(
    display="flex",
    flex_direction="column",
    height="100%",
)

PAGE_BACKGROUND_STYLE = me.Style(
    background=me.theme_var("background"),
    height="100%",
    overflow_y="scroll",
    margin=me.Margin(bottom=20),
)

PAGE_BACKGROUND_PADDING_STYLE = me.Style(
    background=me.theme_var("background"),
    padding=me.Padding(top=24, left=24, right=24, bottom=24),
    display="flex",
    flex_direction="column",
)
