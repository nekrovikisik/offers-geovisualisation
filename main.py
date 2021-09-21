import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import plotly.express as px
import geopandas as gpd
import pandas as pd
from shapely import wkt

token = open(".mapbox_token").read() # you will need your own token

def get_gdf(path):
    df = pd.read_csv(path, index_col=0)
    # df['geometry'] = gpd.GeoSeries.fr(df['geometry'])
    df['geometry'] = df['geometry'].apply(wkt.loads)
    gdf = gpd.GeoDataFrame(df, geometry=df.geometry)
    return gdf

def getChoropleth(df, col):
    fig = px.choropleth_mapbox(
        df, geojson=df['geometry'], color=col,
        locations=df.index,
        # featureidkey="properties.district",
        zoom=6, center={"lat": 55.7536526, "lon": 37.6197863},
        range_color=[0, 100])
    fig.update_layout(
        # margin={"r":0,"t":0,"l":0,"b":0},
        mapbox_accesstoken=token)
    return fig

alldeals_AdmArea = get_gdf('data/alldeals_AdmArea.csv')
alldeals_district = get_gdf('data/alldeals_district.csv')
area_conversion = get_gdf('data/area_conversion.csv')
district_conversion = get_gdf('data/district_conversion.csv')

print(alldeals_AdmArea)
areas = ['AdmArea', 'district']

fig = getChoropleth(alldeals_AdmArea, 'id')
fig1 = getChoropleth(area_conversion, 'conv1')
fig2 = getChoropleth(area_conversion, 'conv2')

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div([
        html.P("Смотреть конверсию по"),
        dcc.RadioItems(
            id='area',
            options=[{'value': x, 'label': x} for x in areas],
            value=areas[0]
        ),
        html.Div([
            html.H3('Количество сделок'),
            html.P('Грязные лиды'),
            dcc.Graph(id="choropleth_count", figure=fig),
        ], style={'width': '33%','display': 'inline-block'}),
        html.Div([
            html.H3('Конверсия'),
            html.P('"замер назначен" →"замер выполнен"'),
            dcc.Graph(id="choropleth_conversion1", figure=fig1)
        ], style={'width': '33%','display': 'inline-block'}),
        html.Div([
            html.H3('Конверсия'),
            html.P('"замер выполнен" → "успешно реализовано"'),
            dcc.Graph(id="choropleth_conversion2", figure=fig2)
        ], style={'width': '33%','display': 'inline-block'})
], className='row')
@app.callback(
    Output("choropleth_count", "figure"),
    Output("choropleth_conversion1", "figure"),
    Output("choropleth_conversion2", "figure"),
    [Input("area", "value")])

def update_fig(area):
    if area == 'AdmArea':
        df1 = alldeals_AdmArea
        df2 = area_conversion
    else:
        df1 = alldeals_district
        df2 = district_conversion

    fig = getChoropleth(df1, 'id')
    fig1 = getChoropleth(df2, 'conv1')
    fig2 = getChoropleth(df2, 'conv2')
    return fig, fig1, fig2


app.run_server(debug=True)
