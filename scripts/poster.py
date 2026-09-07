from __future__ import annotations

import base64
import html
import os

import panel as pn
import segno
from assets_poster.content import JSON_TRANSFORMATION
from assets_poster.content import LEFT_BOTTOM_TEXT
from assets_poster.content import LEFT_MID_TEXT
from assets_poster.content import LEFT_TOP_TEXT
from assets_poster.content import RIGHT_TEXT
from assets_poster.styles import ARROW
from assets_poster.styles import ARROW_STYLES
from assets_poster.styles import CUSTOM_CSS
from assets_poster.styles import HEADER_HEIGHT
from assets_poster.styles import HEADER_WIDTH
from assets_poster.styles import HIST_STYLES
from assets_poster.styles import JSON_STYLES
from assets_poster.styles import MAP_STYLES
from assets_poster.styles import TS_STYLES
from assets_poster.styles import WIDTH_TEXT

pn.extension(raw_css=["nav#header {display: none}"])

qrcode = segno.make_qr("github.com/oceanmodeling/ioc_cleanup")
os.makedirs("./scripts/data", exist_ok=True)
qrcode.save(
    "./scripts/data/qrcode.png",
    scale=5,
    dark="#0F60A8",
    light="#FFFFFF00",
)


def html_(fn: str) -> str:
    with open(fn) as f:
        escaped_html = html.escape(f.read())
        iframe_html = f'<iframe srcdoc="{escaped_html}" style="height:100%; width:100%" frameborder="0"></iframe>'
        return iframe_html


title = pn.pane.Markdown(
    LEFT_TOP_TEXT,
    width=WIDTH_TEXT,
    styles={
        "font-size": "18px",
        "background-color": "#FFFFFF",
    },
)

concepts = pn.pane.Markdown(
    LEFT_MID_TEXT,
    width=WIDTH_TEXT,
    styles={
        "font-size": "18px",
        "margin": "10px",
        "padding": "10px",
        "font-color": "#FFFFFF",
        "background-color": "#D2EBF9",
        "border-color": "#0F60A8",
        "border-radius": "25px",
        "border": "5px",
    },
)
table = pn.pane.Markdown(
    LEFT_BOTTOM_TEXT,
    width=WIDTH_TEXT,
    styles={
        "font-size": "18px",
        "background-color": "#FFFFFF",
    },
)

getting_started = pn.pane.Markdown(
    RIGHT_TEXT,
    width=WIDTH_TEXT,
    styles={"font-size": "18px"},
    stylesheets=[CUSTOM_CSS],
)

json_code = pn.pane.Markdown(
    JSON_TRANSFORMATION,
    width=570,
    stylesheets=[CUSTOM_CSS],
    **JSON_STYLES,
)
ts_raw = pn.pane.HTML(html_("docs/example.html"), **TS_STYLES)
ts_clean = pn.pane.HTML(html_("docs/example_clean.html"), **TS_STYLES)
map_stations = pn.pane.HTML(html_("docs/cleaned_map.html"), **MAP_STYLES)
qrcode_pn = pn.pane.PNG("./scripts/data/qrcode.png")
om_logo = pn.pane.PNG("./scripts/assets_poster/oceanmodeling.png")

with open("./scripts/assets_poster/EU.png", "rb") as f:
    logo_b64 = base64.b64encode(f.read()).decode()

logo_src = f"data:image/png;base64,{logo_b64}"

header = pn.pane.HTML(
    f"""
    <div style="
        position: relative;
        height: {HEADER_HEIGHT}px;
        width: {HEADER_WIDTH}px;
        background-image: linear-gradient(to right, #50B0E7, white);
    ">
        <img
            src="{logo_src}"
            style="
                position: absolute;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                height: {HEADER_HEIGHT}px;
                width: auto;
            "
        />
    </div>
    """,
    width=HEADER_WIDTH,
    height=HEADER_HEIGHT,
)

hist_overlay = pn.pane.HTML(
    html_("docs/coverage_oceans.html"),
    **HIST_STYLES,
)

map_with_hist = pn.Column(
    map_stations,
    hist_overlay,
    styles={"position": "relative"},
)

arrow1 = pn.pane.HTML(ARROW, **ARROW_STYLES)
arrow2 = pn.pane.HTML(ARROW, **ARROW_STYLES)

main = pn.Row(
    pn.Column(
        pn.Row(header),
        pn.Row(
            pn.Column(title, concepts, table),
            map_with_hist,
            pn.Column(getting_started, pn.Row(qrcode_pn, om_logo)),
        ),
        pn.Row(ts_raw, arrow1, json_code, arrow2, ts_clean),
    ),
)

main.save("./docs/assets/poster.html", title="IOC Cleanup Poster EGU26", embed=True)
main.servable()
