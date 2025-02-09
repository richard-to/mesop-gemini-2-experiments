# Mesop Gemini Live Experimental Demos

_Note: These are very rough demos to see how Mesop can be used with the Gemini 2 Live API
with websockets._

The demos here use https://github.com/ghchinoy/studio-scaffold as the initial scaffold.

For a version that performs the web socket connection via Mesop web component, see https://github.com/google/mesop/tree/main/mesop/examples/web_component/gemini_live. That version is more reliable/scalable than the demos here. The main drawback is that it's not really secure to do a direct web socket connection to the Gemini Live API on the JS client since it exposes the API key. To get around that would need to set up a proxy web socket server most likely.

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
