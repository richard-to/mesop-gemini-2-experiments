from typing import Any, Callable

import mesop.labs as mel


@mel.web_component(path="./audio_recorder.js")
def audio_recorder(
  *,
  enabled: bool = False,
  on_data: Callable[[mel.WebEvent], Any],
  on_record: Callable[[mel.WebEvent], Any],
):
  """Records audio and streams audio to the Mesop server.

  This web components is designed to work with `MESOP_WEBSOCKETS_ENABLED=true`.

  The `on_data` event returns continuous chunk of audio in base64-encoded PCM format
  with 16000hz sampling rate. For some reason the Gemini Live API only accepts the PCM
  data 16000hz. At 48000hz, nothing is returned. Perhaps there is a setting to override
  the expected sampling rate when sent to the Gemini Live API. Unfortunately, the docs
  are very sparse right now.

  The data event looks like:

    {
      "data": <base64-encoded-string>
    }
  """
  return mel.insert_web_component(
    name="audio-recorder",
    events={
      "dataEvent": on_data,
      "recordEvent": on_record,
    },
    properties={
      "enabled": enabled,
    },
  )
