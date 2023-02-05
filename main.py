from tkinter import Tk
from tkinter.filedialog import askopenfilename
import xml.etree.ElementTree as ET
import plotly.express as px
import pandas as pd

from os.path import join, split, exists
from os import makedirs

"""
    pyinstaller --onefile --noconsole main.py
"""


def strp_time(_str) -> float:
    """
    Converts string to seconds.ms
    example: "00:01:31.8671660" -> 91.867
    """
    h, m, s = _str.split(":")
    return round(int(h)*3600 + int(m)*60 + float(s), 3)


def strf_time(_flt) -> str:
    """
    Converts seconds.ms to string
    example: 91.867 ->
    """
    res = ""
    s = round(_flt % 60, 3)
    m = int(_flt // 60)
    h = int(_flt // 3600)
    if h != 0:
        res += str(h)+":"
    if m != 0:
        res += str(m)+":"
    res += str(s)
    return res


if __name__ == "__main__":
    Tk().withdraw()  # we don't want a full GUI, so keep the root window from appearing
    filename = askopenfilename()  # show an "Open" dialog box and return the path to the selected file

    if not filename.endswith(".lss"):
        exit()

    filepath, filename = split(filename)
    map_name = filename.split(".")[0]

    tree = ET.parse(join(filepath, filename))
    root = tree.getroot()
    segs = root.find("Segments")

    pb_times, golds, lst_diff, names = [], [], [], []

    for seg in segs:
        pb = seg.find("SplitTimes")[0][0].text
        gold = seg.find("BestSegmentTime")[0].text
        name = seg.find("Name").text

        pb = strp_time(pb)
        pb_segment = round(pb - sum(pb_times), 3)
        gold = strp_time(gold)

        pb_times.append(pb_segment)
        golds.append(gold)
        lst_diff.append(round(pb_segment - gold, 3))
        names.append(name)

    df = pd.DataFrame({"Names": names, "Golds": golds, "PB Times": pb_times, "Difference": lst_diff})

    fig = px.bar(df, x="Names", y=["Difference", "PB Times", "Golds"], title=map_name,
                 color_discrete_sequence=["rgba(0,0,0,0)", "green", "rgba(210, 177, 3, 0.85)"], template="plotly_dark")
    fig.update_traces(hovertemplate=None)
    fig.update_layout(barmode="overlay", hovermode="x unified", yaxis=dict(title="Seconds"), xaxis=dict(title="Split"),
                      legend_title="Legend")

    fig.add_annotation(text=f"SoB: {strf_time(df['Golds'].sum())}",
                       xref="paper", yref="paper", x=1.14, y=0.5, showarrow=False)
    fig.add_annotation(text=f"PB: {strf_time(df['PB Times'].sum())}",
                       xref="paper", yref="paper", x=1.14, y=0.43, showarrow=False)

    if not exists(join(filepath, "graphs")):
        makedirs(join(filepath, "graphs"))
    fig.write_html(join(filepath, "graphs", f"{map_name}.html"))
    fig.show()
