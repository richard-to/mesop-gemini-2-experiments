import mesop as me


def home_content(app_state: me.state):
  with me.box(style=me.Style(margin=me.Margin.all(20))):
    me.text(
      "Mesop Gemini Live Experiments",
      type="headline-4",
      style=me.Style(margin=me.Margin(bottom=18)),
    )
    me.text(
      "This demo contains examples of how to integrate Mesop with Gemini Live.",
      style=me.Style(margin=me.Margin(bottom=15)),
    )
    me.text("Example demos", type="headline-5")

    me.text("Audio demo", type="headline-6")
    me.text(
      "This example shows how we can stream audio input to Gemini Live and return audio output.",
      style=me.Style(margin=me.Margin(bottom=15)),
    )
    me.link(
      text="Audio Demo",
      url="/audio_demo",
      style=_LINK_BUTTON_STYLE,
    )

    me.text("Video demo", type="headline-6")
    me.text(
      "This example shows how we can stream video input to Gemini Live and return audio output.",
      style=me.Style(margin=me.Margin(bottom=15)),
    )
    me.link(
      text="Video Demo",
      url="/video_demo",
      style=_LINK_BUTTON_STYLE,
    )

    me.text("Tool demo", type="headline-6")
    me.text(
      "This example shows how we integrate custom tools that manipulate Mesop state/UI.",
      style=me.Style(margin=me.Margin(bottom=15)),
    )
    me.link(
      text="Tool Demo",
      url="/tool_demo",
      style=_LINK_BUTTON_STYLE,
    )


_LINK_BUTTON_STYLE = me.Style(
  background=me.theme_var("primary"),
  border_radius=5,
  display="inline-block",
  color=me.theme_var("on-primary"),
  margin=me.Margin(bottom=20),
  padding=me.Padding.all(12),
  text_decoration="none",
)
