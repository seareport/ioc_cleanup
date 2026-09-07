from __future__ import annotations

CUSTOM_CSS = """
/* ── Inline code: cyan on dark black ── */
:host p code {
    color: #00e5ff !important;
    background-color: #1a1a1a !important;
    padding: 1px 1px !important;
    border-radius: 3px !important;
}

/* ── Code block background ── */
:host .codehilite,
:host pre {
    background-color: transparent !important;
        padding: 5px;

}
:host .codehilite pre,
:host .codehilite code {
    background-color: #D2EBF9 !important;
    font-size: 90%
}

/* ── JSON syntax colors (Pygments classes) ── */
:host .codehilite .nt { color: #0F60A8 !important; }   /* keys */
:host .codehilite .s2 { color: #777777 !important; }   /* string values */
:host .codehilite .mi { color: #bd93f9 !important; }   /* numbers */
:host .codehilite .kc { color: #19B87F !important; }   /* true/false/null */
:host .codehilite .p  { color: #000000 !important; }   /* punctuation */


/* BASH */
:host .codehilite .ch { color: #777777 !important; }   /* hashbang #!/bin/bash       */
:host .codehilite .c1 { color: #777777 !important; }   /* comments                   */
:host .codehilite .nb { color: #0F60A8 !important; }   /* builtins (cd, echo, export)*/
:host .codehilite .nv { color: #19B87F !important; }   /* variables ($VAR)           */
:host .codehilite .k  { color: #0F60A8 !important; }   /* keywords (if, then, for)   */
:host .codehilite .o  { color: #000000 !important; }   /* operators (&&, =)          */
/* .s2  string  - already set above     */
/* .m   number  - see below             */
:host .codehilite .m  { color: #bd93f9 !important; }   /* numbers                    */
/* .p   punctuation - already set above */

/* PYTHON */
:host .codehilite .kn { color: #0F60A8 !important; }   /* import / from              */
/* .k   keyword  - already set above    */
:host .codehilite .nn { color: #19B87F !important; }   /* module names               */
:host .codehilite .nc { color: #19B87F !important; }   /* class names                */
:host .codehilite .nf { color: #0F60A8 !important; }   /* function names             */
:host .codehilite .fm { color: #0F60A8 !important; }   /* magic methods (__init__)   */
:host .codehilite .n  { color: #000000 !important; }   /* variables / generic names  */
/* .nb  builtins - already set above    */
:host .codehilite .bp { color: #bd93f9 !important; }   /* self                       */
:host .codehilite .nd { color: #777777 !important; }   /* decorators (@staticmethod) */
/* .o   operator - already set above    */
:host .codehilite .ow { color: #0F60A8 !important; }   /* operator words (in, is, not, and) */
/* .s2  strings  - already set above    */
:host .codehilite .sa { color: #777777 !important; }   /* string prefix (f in f"")   */
:host .codehilite .si { color: #19B87F !important; }   /* f-string interpolation {}  */
:host .codehilite .sd { color: #777777 !important; }   /* docstrings                 */
/* .mi  integer  - already set above    */
:host .codehilite .mf { color: #bd93f9 !important; }   /* floats                     */
/* .kc  constants - already set above   */
/* .c1  comments  - already set above   */

"""

JSON_STYLES = {
    "styles": {
        "font-size": "18px",
        "margin-right": "-60px",
        "margin-left": "-0px",
    },
}

WIDTH_TEXT = 800
HEADER_HEIGHT = 200
HEADER_WIDTH = 3200
TS_HEIGHT = 718

BORDER_BLUE = {
    "styles": {
        "border": "5px",
        "border-style": "solid",
        "border-color": "#0F60A8",
        "border-radius": "25px",
        "box-sizing": "border-box",
        "overflow": "hidden",
    },
}

TS_STYLES = {
    "width": int(TS_HEIGHT * 1.665),
    "height": TS_HEIGHT,
    **BORDER_BLUE,
}
MAP_STYLES = {
    "width": 1750,
    "height": 1250,
}

ARROW_HEIGHT = 110
ARROW_WIDTH = 60

# viewBox width=ARROW_WIDTH, height=ARROW_HEIGHT in internal units
# Scale polygon points accordingly - shaft is ~57% of height, head is ~43%
shaft_end_y = 20  # where shaft ends / head begins (out of 100)
shaft_top = 30  # shaft top edge (out of 100, centered)
shaft_bot = 70  # shaft bottom edge (out of 100, centered)
shaft_len = 70  # shaft bottom edge (out of 100, centered)

ARROW = f"""
    <div style="
        display: flex;
        align-items: center;
        justify-content: center;
        height: 100%;
        min-height: {TS_HEIGHT}px;
    ">
        <svg xmlns="http://www.w3.org/2000/svg" width="{ARROW_WIDTH}" height="{ARROW_HEIGHT}" viewBox="0 0 70 70">
            <polygon
                points="0,{shaft_top} {shaft_end_y},{shaft_top} {shaft_end_y},0 {shaft_len},50 {shaft_end_y},100 {shaft_end_y},{shaft_bot} 0,{shaft_bot}"
                fill="#D2EBF9"
                stroke="#0F60A8"
                stroke-width="3"
                stroke-linejoin="round"
            />
        </svg>
    </div>
    """
ARROW_STYLES = {
    "margin": (0, 10),
    "width": ARROW_WIDTH + 20,
    "height": ARROW_HEIGHT,
}

TABLE_STYLES = """
<style>
table td, table th {
    text-align: left !important;
}
</style>
"""

HIST_STYLES = {
    "styles": {
        "position": "absolute",
        "top": "36px",
        "right": "40px",
        "z-index": "1000",
        "background-color": "rgba(255,255,255,0.6)",
        "border-radius": "10px",
        "border": "1px solid #ccc",
        "padding": "0px",
    },
    "width": 670,
    "height": 380,
}
