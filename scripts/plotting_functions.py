import pandas as pd
import altair as alt
import streamlit as st


def chart_curves(df, taxa_on, premio_limpo=False):
    em_space = "\u2003"

    df = df.copy()
    # df["Date"] = df["Date"].dt.strftime("%Y/%m/%d")

    if st.session_state.titulo=='NTN-B':
        label_titulo = 'Taxa Real'
        coluna_taxa = 'IndicativeRate'

    elif st.session_state.titulo=='LFT':
        label_titulo = 'prêmio'
        coluna_taxa = 'IndicativeRate'

    elif st.session_state.titulo=='LTN':
        if taxa_on:
            label_titulo = 'taxa'
            coluna_taxa = 'IndicativeRate'
        else:
            label_titulo = 'prêmio'
            coluna_taxa = 'premio'

    elif st.session_state.titulo=='NTN-F':
        if taxa_on:
            label_titulo = 'taxa'
            coluna_taxa = 'IndicativeRate'
        else:
            if not premio_limpo:
                label_titulo = 'prêmio'
                coluna_taxa = 'premio'
            else:
                label_titulo = 'prêmio limpo'
                coluna_taxa = 'premio'
                # coluna_taxa = 'premio_limpo'

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
                f"{coluna_taxa}:Q",
                scale=alt.Scale(
                    domain=[
                        df[coluna_taxa].min(),
                        df[coluna_taxa].max(),
                    ],
                ),
                axis=alt.Axis(
                    title=f"{label_titulo}",
                    labelFontSize=13,
                    titleFontSize=16,
                    format=".2f",
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
                f"{coluna_taxa}:Q",
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
        height=350,
        title="Curvas"#: de {start_date} até {end_date}",
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


def chart_lines(df_interpolation, venc_interp, taxa=True, em_bps=False):

    # Create a selection that chooses the nearest point & selects based on x-value
    # nearest = alt.selection_point(nearest=True, on="pointerover", fields=["premio"], empty=False)

    if st.session_state.titulo=='NTN-B':
        label_titulo = 'Taxa Real'
        coluna_taxa = 'premio'

    elif st.session_state.titulo=='LFT':
        label_titulo = 'prêmio'
        coluna_taxa = 'premio'
    else:
        if taxa==True:
            label_titulo = 'taxa'
            coluna_taxa = 'premio'
        else:
            label_titulo = 'prêmio'
            coluna_taxa = 'premio'

    if em_bps:
        label_titulo=f'Variação {label_titulo} em bps'
        coluna_taxa='basis_point_change'

    chart = alt.Chart(df_interpolation, title=f'Vértice de {venc_interp} anos').mark_line(interpolate='monotone', size=3).encode(
            alt.X('Date:T', title='Data'),
            alt.Y(
                f'{coluna_taxa}:Q',
                title=label_titulo,
                scale=alt.Scale(
                    domain=[
                        df_interpolation[f"{coluna_taxa}"].min(),
                        df_interpolation[f"{coluna_taxa}"].max(),
                    ],),
                ),
            color = alt.Color('vertice:N').scale(scheme='dark2'),
            tooltip = ['Date:T', 'premio']
            ).properties(width=600, height=520)

    # Transparent selectors across the chart. This is what tells us
    # the x-value of the cursor
    # selectors = alt.Chart(df_interpolation).mark_point().encode(x="Date:T",opacity=alt.value(0),).add_params(nearest)
    #
    # Draw points on the line, and highlight based on selection
    # points = chart.mark_point().encode(opacity=alt.condition(nearest, alt.value(1), alt.value(0)))

    # Draw text labels near the points, and highlight based on selection
    # text = chart.mark_text(align="left", dx=5, dy=-5).encode(text=alt.condition(nearest, "premio:Q", alt.value(" ")))

    # Draw a rule at the location of the selection
    # rules = alt.Chart(df_interpolation).mark_rule(color="gray").encode(x="Date:T").transform_filter(nearest)

    # chart = rules + chart+ selectors+ points+ text

    chart = (
        chart.configure_title(fontSize=23, anchor="start")
        .configure_axis(labelFontSize=16, titleFontSize=16, grid=False)
        .configure_legend(labelFontSize=16, titleFontSize=16)
    )

    return chart
