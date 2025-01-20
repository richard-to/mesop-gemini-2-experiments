# Mesop Gemini Live Experimental Demos

_Note: These are very rough demos to see how Mesop can be used with the Gemini 2 Live API
with websockets._

The demos here use https://github.com/ghchinoy/studio-scaffold as the initial scaffold.

## Usage demos

Mesops websockets mode is required to use these demos. In addition, you'll need Python
3.11+ since some of the async behavior is not working with 3.10 at the moment.

```
GOOGLE_API_KEY=YOUR_API_KEY MESOP_WEBSOCKETS_ENABLED=true mesop main.py
```

## Example demos

Here is an overview of the current demos.

### Audio demo

This example shows how we can stream audio input to Gemini Live and return audio output.

### Video demo

This example shows how we can stream video input to Gemini Live and return audio output.

### Tool demo

This example shows how we integrate custom tools that manipulate Mesop state/UI.

## Known issues

- Web socket connection sometimes starts randomly disconnecting. This seems like maybe
  it is a quota issue.
- Currently no real error handling for error cases, so if something breaks, just stop
  the Mesop server and start it again. And reload your web page.
