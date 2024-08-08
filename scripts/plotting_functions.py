import pandas as pd
import altair as alt
import streamlit as st


def chart_curves(df, ):
    em_space = "\u2003"

    df = df.copy()
    # df["Date"] = df["Date"].dt.strftime("%Y/%m/%d")

    if st.session_state.titulo=='NTN-B':
        label_titulo = 'Taxa Real'
    elif st.session_state.titulo=='LFT':
        label_titulo = 'Prêmio'
    else:
        label_titulo = 'Taxa'

    start_date = st.session_state.start_date#.strftime("%d/%m/%Y")
    end_date = st.session_state.end_date#.strftime("%d/%m/%Y")

    # interval selection
    interval_sel = alt.selection(type="interval", encodings=["x"])

    base = alt.Chart(df)

    chart_line = (
        # alt.Chart(
        #     df,
        #     title=f"DI Curves: from {start_date} to {end_date}",
        # )
        base.transform_filter(interval_sel)
        .mark_line(interpolate="monotone", size=2)
        .encode(
            alt.X(
                "Days to Expiration:Q",
                scale=alt.Scale(
                    domain=[
                        df["Days to Expiration"].min(),
                        df["Days to Expiration"].max(),
                    ],
                ),
                axis=alt.Axis(
                    title="Vencimento (anos)",
                    labelFontSize=12,
                    titleFontSize=16,
                    format=".1f",
                    ticks=True,
                    # tickMinStep=1,
                    tickCap="round",
                    tickSize=10,
                    # tickCount=df["Days to Expiration"].max() * 2,
                    # format="%d-%b-%y",
                ),
            ),
            alt.Y(
                "IndicativeRate:Q",
                scale=alt.Scale(
                    domain=[
                        df["IndicativeRate"].min(),
                        df["IndicativeRate"].max(),
                    ],
                ),
                axis=alt.Axis(
                    title=f"{label_titulo}",
                    labelFontSize=13,
                    titleFontSize=16,
                    format=".1f",
                    labels=True,
                ),
            ),
            color=alt.Color(
                "Date:Q",
                scale=alt.Scale(scheme="redyellowblue", reverse=True),
                sort=alt.EncodingSortField("Date", order="descending"),
                legend=None,
            ),
            tooltip=[
                "Date:T",
                "Days to Expiration:Q",
                "IndicativeRate:Q",
            ],
        )
    )

    chart_legend = (
        # alt.Chart(df)
        base.mark_rect().encode(
            alt.X(
                "yearmonthdate(Date):O",
                axis=alt.Axis(
                    title=None,
                    ticks=False,
                    labelFontSize=10,
                    format="%d-%b-%y",
                    labelPadding=3,
                ),
            ),
            color=alt.Color(
                "Date:Q",
                legend=None,
                scale=alt.Scale(scheme="redyellowblue", reverse=False),
                sort=alt.EncodingSortField("Date", order="descending"),
            ),
            tooltip=["Date:T"],
        )
    )

    chart_legend = chart_legend.add_params(interval_sel).properties(
        width=800,
        height=30,
        title={
            "text": "Select a date range below by dragging your mouse",
            "fontSize": 10,
            "anchor": "start",
            "dy": 20,
        },
    )

    chart_line = chart_line.properties(
        width=800,
        height=200,
        title=f"Curvas {st.session_state.titulo}"#: de {start_date} até {end_date}",
    )

    chart_total = chart_line & chart_legend
    # chart_total = alt.hconcat(chart_total, chart_hist)
    # chart_total = chart_line & chart_legend
    chart_total = (
        chart_total.configure_title(fontSize=23, anchor="start")
        .configure_axis(labelFontSize=16, titleFontSize=16, grid=False)
        .configure_legend(labelFontSize=16, titleFontSize=16)
    )

    return chart_total


