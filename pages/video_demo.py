"""Demo of using Gemini 2 API with websockets and Mesop.

This demo focuses only on video input and audio output.

In this demo you can type in questions about the video input, such as what do you see?

You could also take this a step further and add audio input as well.

Ideally, we'd use WebRTC, but for demos, websockets should be good enough for handling
the streaming video input and audio output.

This demo is based off the example at:
https://github.com/google-gemini/cookbook/blob/main/gemini-2/websockets/live_api_starter.py
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
from web_components.audio_player import (
  audio_player,
)
from web_components.video_recorder import (
  video_recorder,
)


_HOST = "generativelanguage.googleapis.com"
_MODEL = "gemini-2.0-flash-exp"


_API_KEY = os.getenv("GOOGLE_API_KEY")
_GEMINI_BIDI_WEBSOCKET_URI = f"wss://{_HOST}/ws/google.ai.generativelanguage.v1alpha.GenerativeService.BidiGenerateContent?key={_API_KEY}"


_GEMINI_LIVE_LOOP_MAP = {}


class GeminiLiveLoop:
  def __init__(self):
    self.audio_in_queue = None
    self.out_queue = None

    self.ws = None

  async def startup(self):
    setup_msg = {"setup": {"model": f"models/{_MODEL}"}}
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


@me.stateclass
class State:
  data: bytes = b""
  session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
  prompt: str = ""
  gemini_connection_enabled: bool = False
  video_recorder_enabled: bool = False
  audio_player_enabled: bool = False


def video_demo_content(app_state: me.state):
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
        "Step 3a: Start recording video",
        type="headline-5",
        style=me.Style(margin=me.Margin.symmetric(vertical=15)),
      )
      video_recorder(
        on_data=stream_video_input, enabled=state.video_recorder_enabled, on_record=on_video_record
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


def on_audio_play(e: mel.WebEvent):
  me.state(State).audio_player_enabled = True


def on_video_record(e: mel.WebEvent):
  me.state(State).video_recorder_enabled = True


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


async def stream_video_input(e: mel.WebEvent):
  """Video input is forwarded to Gemini."""
  global _GEMINI_LIVE_LOOP_MAP
  state = me.state(State)
  if state.session_id in _GEMINI_LIVE_LOOP_MAP:
    await _GEMINI_LIVE_LOOP_MAP[state.session_id].send_video_direct(e.value["data"])


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
