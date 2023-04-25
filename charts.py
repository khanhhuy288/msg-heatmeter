import plotly.graph_objs as go
from plotly.subplots import make_subplots


def create_load_profile_chart(load_data):
    hour_values = list(range(0, 24))
    hovertemplate = '%{y:.2f} kW'

    load_fig = go.Figure()

    for name, load in load_data.items():
        load_fig.add_trace(
            go.Scatter(
                x=hour_values,
                y=load,
                mode='lines',
                name=name,
                hovertemplate=hovertemplate
            )
        )

    load_fig.update_layout(
        title=dict(text='Load Profile'),
        xaxis=dict(title='Time (Hour)', dtick=1),
        yaxis=dict(title='Load (kW)'),
        hovermode='x'
    )

    return load_fig


def create_temperature_energy_chart(monthly_temp, monthly_energy):
    temp_energy_fig = make_subplots(specs=[[{"secondary_y": True}]])

    temp_trace = go.Scatter(x=monthly_temp.index, y=monthly_temp, mode='lines', name='Average Temperature',
                            hovertemplate='%{y:.1f}°C<extra></extra>')
    energy_trace = go.Scatter(x=monthly_energy.index, y=monthly_energy, mode='lines', name='Energy',
                              hovertemplate='%{y:.2f} MWh<extra></extra>')

    temp_energy_fig.add_trace(temp_trace, secondary_y=False)
    temp_energy_fig.add_trace(energy_trace, secondary_y=True)

    temp_energy_fig.update_layout(
        title=dict(text="Monthly Average Temperature and Total Energy"),
        showlegend=False,
        hovermode="x"
    )

    temp_energy_fig.update_xaxes(title_text="Month", tickangle=-90, tickformat='%m.%Y', showticklabels=True, dtick='M1')
    temp_energy_fig.update_yaxes(title_text="Average Temperature (°C)", secondary_y=False, showgrid=True,
                                 title_font=dict(color='blue'), dtick=2.5)
    temp_energy_fig.update_yaxes(title_text="Energy (MWh)", secondary_y=True, showgrid=False, title_font=dict(color='red'))

    temp_energy_fig.update_traces(showlegend=False)

    return temp_energy_fig


def create_temperature_chart(temp_data):
    hour_values = list(range(0, 24))
    hovertemplate = '%{y:.1f}°C'

    temp_fig = go.Figure()

    for name, temp in temp_data.items():
        temp_fig.add_trace(
            go.Scatter(
                x=hour_values,
                y=temp,
                mode='lines',
                name=name,
                hovertemplate=hovertemplate
            )
        )

    temp_fig.update_layout(
        title=dict(text='Hourly Temperature'),
        xaxis=dict(title='Time (Hour)', dtick=1),
        yaxis=dict(title='Temperature (°C)'),
        showlegend=True,
        hovermode='x'
    )

    return temp_fig
