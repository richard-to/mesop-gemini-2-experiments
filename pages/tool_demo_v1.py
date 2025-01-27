"""Tool usage demo of using Gemini 2 API with websockets and Mesop.

This demo focuses on tool usage and integration with Mesop.

Here we create three boxes. The user can click on the box and Gemini will respond with
the question in the box.

In addition the user can use text input or audio input to ask Gemini to open the box
and read the contents inside the box.

The state of the boxes will change as the user and Gemini interact with the boxes.

This demo requires headphones since system audio cancellation isn't implemented.

This demo is based off the examples at:

- https://github.com/google-gemini/cookbook/blob/main/gemini-2/websockets/live_api_starter.py
- https://github.com/google-gemini/cookbook/blob/main/gemini-2/live_api_tool_use.ipynb
"""

import asyncio
import base64
import json
import os
import traceback
import uuid
from dataclasses import field

from websockets.asyncio.client import connect

import mesop as me
import mesop.labs as mel
from web_components_v1.audio_player import (
  audio_player,
)
from web_components_v1.audio_recorder import (
  audio_recorder,
)


_HOST = "generativelanguage.googleapis.com"
_MODEL = "gemini-2.0-flash-exp"


_API_KEY = os.getenv("GOOGLE_API_KEY")
_GEMINI_BIDI_WEBSOCKET_URI = f"wss://{_HOST}/ws/google.ai.generativelanguage.v1alpha.GenerativeService.BidiGenerateContent?key={_API_KEY}"


_GEMINI_LIVE_LOOP_MAP = {}

_SYSTEM_INSTRUCTIONS = """
You are an agent that helps people select boxes.

You have access to the following tool:
- get_box: Gets the contents of a box by name.

Rules:
- If the user does not select a box. Tell them that the user must select a box name.
- The user will specify the name of the box. Use the get_box tool. The box will return a
  question. Ask the user the question.
""".strip()


@me.stateclass
class State:
  data: bytes = b""
  session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
  prompt: str = ""
  gemini_connection_enabled: bool = False
  audio_recorder_enabled: bool = False
  audio_player_enabled: bool = False
  boxes: dict[str, str] = field(
    default_factory=lambda: {
      "green": "Who is the first president?",
      "blue": "What is the capital of China?",
      "red": "What is the tallest mountain?",
    }
  )
  opened_boxes: set[str] = field(default_factory=set)


class GeminiLiveLoop:
  def __init__(self):
    self.audio_in_queue = None
    self.out_queue = None

    self.ws = None

  async def startup(self):
    setup_msg = {
      "setup": {
        "model": f"models/{_MODEL}",
        "system_instruction": {"role": "user", "parts": [{"text": _SYSTEM_INSTRUCTIONS}]},
        "tools": [
          {
            "functionDeclarations": [
              {
                "name": "pick_box",
                "description": "Picks the box by name",
                "parameters": {
                  "type": "OBJECT",
                  "properties": {"box_name": {"type": "STRING", "description": "Name of the box"}},
                  "required": ["box_name"],
                },
              }
            ]
          }
        ],
        "generation_config": {
          "response_modalities": ["audio"],
          "speech_config": {"voice_config": {"prebuilt_voice_config": {"voice_name": "Puck"}}},
        },
      }
    }
    await self.ws.send(json.dumps(setup_msg))
    raw_response = await self.ws.recv(decode=False)
    json.loads(raw_response.decode("ascii"))

  async def send_video_direct(self, data):
    """Sends video input chunks to Gemini."""

    msg = {
      "realtime_input": {
        "media_chunks": [
          {
            "data": data,
            "mime_type": "image/jpeg",
          }
        ]
      }
    }

    await self.ws.send(json.dumps(msg))

  async def send_audio_direct(self, data):
    """Sends audio input chunks to Gemini.

    - Audio chunks need to be sent with a sample rate of 16000hz and be in PCM format.
    - The audio data needs to be base64 encoded since we're using JSON.
    """
    msg = {
      "realtime_input": {
        "media_chunks": [
          {
            "data": data,
            "mime_type": "audio/pcm",
          }
        ]
      }
    }
    await self.ws.send(json.dumps(msg))

  async def send_text_direct(self, text):
    """Sends text input to Gemini."""
    msg = {
      "client_content": {
        "turn_complete": True,
        "turns": [{"role": "user", "parts": [{"text": text}]}],
      }
    }
    await self.ws.send(json.dumps(msg))

  async def receive_audio(self):
    """Process the audio responses returned by Gemini"""
    async for raw_response in self.ws:
      # Other things could be returned here, but we'll ignore those for now.
      response = json.loads(raw_response.decode("ascii"))
      try:
        b64data = response["serverContent"]["modelTurn"]["parts"][0]["inlineData"]["data"]
      except KeyError:
        pass
      else:
        pcm_data = base64.b64decode(b64data)
        self.audio_in_queue.put_nowait(pcm_data)

      try:
        turn_complete = response["serverContent"]["turnComplete"]
      except KeyError:
        pass
      else:
        if turn_complete:
          # If you interrupt the model, it sends an end_of_turn.
          # For interruptions to work, we need to empty out the audio queue
          # Because it may have loaded much more audio than has played yet.
          while not self.audio_in_queue.empty():
            self.audio_in_queue.get_nowait()

      tool_call = response.pop("toolCall", None)
      if tool_call is not None:
        await self.handle_tool_call(tool_call)

  async def handle_tool_call(self, tool_call):
    state = me.state(State)
    for fc in tool_call["functionCalls"]:
      if fc["name"] == "pick_box":
        response = ""
        if fc["args"]["box_name"] not in state.boxes:
          response = "No box found"
        elif fc["args"]["box_name"] in state.opened_boxes:
          response = "You already opened that box"
        else:
          response = state.boxes[fc["args"]["box_name"]]
          state.opened_boxes.add(fc["args"]["box_name"])

        msg = {
          "tool_response": {
            "function_responses": [
              {
                "id": fc["id"],
                "name": fc["name"],
                "response": {
                  "result": response,
                },
              }
            ]
          }
        }
        await self.ws.send(json.dumps(msg))

  async def run(self):
    """Yields audio chunks off the input queue."""
    try:
      async with (
        await connect(
          _GEMINI_BIDI_WEBSOCKET_URI,
          additional_headers={"Content-Type": "application/json"},
        ) as ws,
        asyncio.TaskGroup() as tg,
      ):
        self.ws = ws
        await self.startup()

        self.audio_in_queue = asyncio.Queue()

        tg.create_task(self.receive_audio())

        while True:
          bytestream = await self.audio_in_queue.get()
          yield bytestream

    except asyncio.CancelledError:
      pass
    except ExceptionGroup as EG:
      traceback.print_exception(EG)


def tool_demo_content_v1(app_state: me.state):
  state = me.state(State)
  with me.box(style=me.Style(margin=me.Margin.all(20))):
    me.text(
      "You will need to wear headphones since echo cancellation may or may not be working.",
      style=me.Style(font_style="italic", margin=me.Margin(bottom=15)),
    )

    me.text("Step 1: First start the Gemini Live API", type="headline-5")
    if not state.gemini_connection_enabled:
      me.button(
        "Start connection to Gemini Live API",
        on_click=initialize_gemini_api,
        type="flat",
        color="primary",
      )
    else:
      me.text("Gemini Live API connected")

    if state.gemini_connection_enabled:
      me.text(
        "Step 2: Next initalize the audio player",
        type="headline-5",
        style=me.Style(margin=me.Margin.symmetric(vertical=15)),
      )
      audio_player(data=state.data, enabled=state.audio_player_enabled, on_play=on_audio_play)

    if state.audio_player_enabled:
      me.text(
        "Step 3a: Start recording audio",
        type="headline-5",
        style=me.Style(margin=me.Margin.symmetric(vertical=15)),
      )
      audio_recorder(
        on_data=stream_audio_input, enabled=state.audio_recorder_enabled, on_record=on_audio_record
      )

    if state.audio_player_enabled:
      me.text(
        "Step3b: You can also enter text",
        type="headline-5",
        style=me.Style(margin=me.Margin.symmetric(vertical=15)),
      )
      me.input(
        value=state.prompt,
        appearance="outline",
        on_blur=on_input_blur,
        style=me.Style(margin=me.Margin(right=10)),
      )
      me.button("Send prompt", type="flat", color="primary", on_click=send_text_input)

    me.text(
      "Pick a box",
      type="headline-5",
      style=me.Style(margin=me.Margin.symmetric(vertical=15)),
    )
    for label, question in state.boxes.items():
      with me.box(
        key=label,
        on_click=click_box,
        style=me.Style(
          background=label,
          cursor="pointer",
          padding=me.Padding.all(15),
          margin=me.Margin(bottom=20),
        ),
      ):
        if label in state.opened_boxes:
          me.text(question, style=me.Style(color="#fff", text_align="center"))
        else:
          me.text(label, style=me.Style(color="#fff", text_align="center", font_weight="bold"))


def on_audio_play(e: mel.WebEvent):
  me.state(State).audio_player_enabled = True


def on_audio_record(e: mel.WebEvent):
  me.state(State).audio_recorder_enabled = True


async def initialize_gemini_api(e: me.ClickEvent):
  """Initializes a long running event handler to send audio response data to the client."""
  global _GEMINI_LIVE_LOOP_MAP
  state = me.state(State)
  state.gemini_connection_enabled = True
  yield
  if state.session_id not in _GEMINI_LIVE_LOOP_MAP:
    _GEMINI_LIVE_LOOP_MAP[state.session_id] = GeminiLiveLoop()
    async for bytestream in _GEMINI_LIVE_LOOP_MAP[state.session_id].run():
      me.state(State).data = bytestream
      yield


async def stream_audio_input(e: mel.WebEvent):
  """Audio input is forwarded to Gemini which handles the voice activity detection.

  Unfortunately it does not seem to handle cancellation of the system audio, so we need
  to use headphones for simplicity here.
  """
  global _GEMINI_LIVE_LOOP_MAP
  state = me.state(State)
  if state.session_id in _GEMINI_LIVE_LOOP_MAP:
    await _GEMINI_LIVE_LOOP_MAP[state.session_id].send_audio_direct(e.value["data"])


def on_input_blur(e: me.InputBlurEvent):
  state = me.state(State)
  state.prompt = e.value


async def send_text_input(e: me.ClickEvent):
  """We can also send normal text prompts to Gemini."""
  global _GEMINI_LIVE_LOOP_MAP
  state = me.state(State)
  if state.session_id in _GEMINI_LIVE_LOOP_MAP and state.prompt:
    await _GEMINI_LIVE_LOOP_MAP[state.session_id].send_text_direct(state.prompt)
    state.prompt = ""


async def click_box(e: me.ClickEvent):
  global _GEMINI_LIVE_LOOP_MAP
  state = me.state(State)
  text = "I want to pick the box with the name " + e.key
  if state.session_id in _GEMINI_LIVE_LOOP_MAP:
    await _GEMINI_LIVE_LOOP_MAP[state.session_id].send_text_direct(text)
