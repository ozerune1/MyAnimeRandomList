import os
from dotenv import load_dotenv
import gradio as gr
from gradio_rangeslider import RangeSlider
from scripts.mal import get_random
from scripts.api import generate_env

genres = ['Action', 'Adult Cast', 'Adventure', 'Anthropomorphic', 'Avant Garde', 'Award Winning', 'Boys Love', 'CGDCT', 'Childcare', 'Combat Sports', 'Comedy', 'Crossdressing', 'Delinquents', 'Detective', 'Drama', 'Ecchi', 'Fantasy', 'Girls Love', 'Gore', 'Gourmet', 'Harem', 'Hentai', 'High Stakes Game', 'Historical', 'Horror', 'Idols (Female)', 'Idols (Male)', 'Iyashikei', 'Josei', 'Kids', 'Love Polygon', 'Love Status Quo', 'Mahou Shoujo', 'Mecha', 'Medical', 'Music', 'Mystery', 'Mythology', 'Organized Crime', 'Otaku Culture', 'Parody', 'Performing Arts', 'Pets', 'Psychological', 'Racing', 'Reverse Harem', 'Romance', 'School', 'Sci-Fi', 'Seinen', 'Shoujo', 'Shounen', 'Slice of Life', 'Sports', 'Strategy Game', 'Supernatural', 'Video Game']

def update_checkbox_interactivity(include, exclude):
  new_exclude_choices = [g for g in genres if g not in include]
  new_include_choices = [g for g in genres if g not in exclude]
  return gr.update(choices=new_include_choices, value=include), gr.update(choices=new_exclude_choices, value=exclude)

if not os.path.isfile(".env"):
  generate_env()

load_dotenv()

with gr.Blocks() as demo:
  with gr.Row():
    name = gr.Textbox(label="Username")
    list_type = gr.Radio(
      label="List",
      choices=[
        "All",
        "Watching",
        "Completed",
        "On-Hold",
        "Dropped",
        "Plan to Watch"
      ],
      value = "All"
    )

    types = ['TV', 'Movie', 'ONA', 'TV Special', 'Special', 'OVA', 'Hentai']

    media_type = gr.CheckboxGroup(
      label="Type",
      choices=types,
      value=types 
    )

  with gr.Row():
    score = RangeSlider(
      label="Score",
      minimum=1,
      maximum=10,
      step=0.01,
      value=(1, 10),
      interactive=True
    )
    year = RangeSlider(
      label="Year",
      minimum=1917,
      maximum=2026,
      step=1,
      value=(1917, 2026),
      interactive=True
    )
    episodes = RangeSlider(
      label="Episodes",
      minimum=1,
      maximum=10000,
      step=1,
      value=(1, 10000),
      interactive=True
    )

  with gr.Row():
    include = gr.CheckboxGroup(
      label="Include",
      choices=genres
    )
    exclude = gr.CheckboxGroup(
      label="Exclude",
      choices=genres
    )

  with gr.Row():
    amount = gr.Slider(
      label = "Max List Size",
      minimum = 1,
      maximum = 100,
      value = 10,
      step = 1
    )

    sequels = gr.Radio(
      label = "Sequels",
      choices = ["Yes", "No", "Exclusively"],
      value = "Yes"
    )

    button = gr.Button(value="Randomize")

  gallery = gr.Gallery(
    label="Random List",
    interactive = False,
    rows = 10,
    columns = 10,
    object_fit = "contain"
  )

  # When either checkbox group changes, update both.
  include.change(
    update_checkbox_interactivity,
    inputs=[include, exclude],
    outputs=[include, exclude]
  )
  exclude.change(
    update_checkbox_interactivity,
    inputs=[include, exclude],
    outputs=[include, exclude]
  )

  button.click(fn=get_random, inputs = [name, list_type, media_type, score, year, episodes, include, exclude, amount, sequels], outputs=gallery)

demo.launch()
