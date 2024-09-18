from dash import Dash
from dash import html, dcc, Output, Input
import plotly.express as px
import plotly.graph_objects as go
from readfile import *

# List of all aptions for the radio button
all_generos = ['Feminino', 'Masculino', 'Feminino e Masculino']

# Function to return the dataframe and the color based on the selected genre
def return_df_genero(selected_genero):
    if selected_genero == "Feminino":
        df = df_paris_women.copy()
        color = ["red"]
    elif selected_genero == "Masculino":
        df = df_paris_men.copy()
        color = ["blue"]
    elif selected_genero == "Feminino e Masculino":
        df = df_paris_geral.copy()
        color = ["blue", "red"]
    else:
        df = pd.DataFrame()  # Default empty dataframe

    return df, color

# Inicializing the Dash app
app = Dash(__name__)

# Defining the layout of the app
app.layout = html.Div([
    # Title of the app
    html.H1(children='Dados de Vôlei nas Olimpíadas de Paris', style={'color': '#117029'}),
    # Radio button to select the genre
    dcc.RadioItems(
        all_generos, # List of all options
        'Feminino e Masculino', # Default Button
        id='generos-radio' # ID of the radio button
    ),
    # --------------- Divs All countries ----------------
    # Div to show the pie chart all countries
    html.Div([
        # Graph to show the pie chart
        dcc.Graph(id='pie_chart_all_countries')
    ]),
    html.Div([
        # Graph to show the scatter chart
        dcc.Graph(id='scatter_chart')
    ]),
    html.Div([
        # Graph to show the stacked bars chart
        dcc.Graph(id='scatter_chart_attacks_blocks')
    ]),
    html.Div([
        # Graph to show the stacked bars chart
        dcc.Graph(id='stacked_bars_chart') # all countries
    ]),
    # -------------------- Divs by country --------------------
    # Div to show the pie chart
    html.Div([
        # Dropdown to select the country (The options of countries will be based on the selected genre)
        dcc.Dropdown(
            id="country"
        ),
        # Graph to show the pie chart
        dcc.Graph(id='pie_chart')
    ]),
    # ---------------- Divs all countries: PS - Ainda tentar fazer por país ----------------
    # html.Div([
    #     # Graph to show the scatter chart
    #     dcc.Graph(id='scatter_chart')
    # ]),
    # html.Div([
    #     # Graph to show the stacked bars chart
    #     dcc.Graph(id='scatter_chart_attacks_blocks')
    # ]),
    # ---------------- Divs by player ----------------
    # Div to show the player statistics
    html.Div([
        # Dropdown to select the player (The options of players will be based on the selected genre and country)
        dcc.Dropdown(
            id="player"
        ),
        # Graph to show the player statistics
        dcc.Graph(id='players_chart')
    ]),
])

# Callback to update the pie chart of all countries
@app.callback(
    Output("pie_chart_all_countries", "figure"),
    Input("generos-radio", "value")
)
def generate_pie_chart_all_countries(selected_genero):
    df, _ = return_df_genero(selected_genero)

    labels = ['Ataque', 'Bloqueio', 'Saque']
    sizes = [
        df['Attack-Points'].sum(),
        df['Block-Points'].sum(),
        df['Serve-Points'].sum()
    ]

    fig = px.pie(values=sizes, names=labels, hole=0.3)
    # Update the traces to change the colors of the percentage numbers and add white lines between divisions
    fig.update_traces(
        textinfo='percent',
        textfont=dict(color='white'),  # Change the color and size of the percentage numbers
        marker=dict(
            line=dict(color='white', width=3)  # Add white lines between the divisions
        )
    )

    # Update the layout
    fig.update_layout(
        showlegend=True,
        title = "Distribuição de Pontos por Categoria de todos os Países",
        title_x=0.5
    )
    
    return fig

# Callback to update the stacked bars chart based on the selected genre
@app.callback(
    Output("stacked_bars_chart", "figure"),
    Input("generos-radio", "value")
)
def generate_stacked_bars(selected_genero):
    df, _ = return_df_genero(selected_genero)
    metrics = ['Points-attacks', 'Succesful-blocks', 'Successful-dig', 'Succesful-receive', 'serve-points', 'Successful-setter', "Team"]
    name_categories = ['Pontos de Ataque', 'Pontos de Bloqueio', 'Sucesso de Defesa', 'Sucesso de Recepção de Saque', 'Pontos de Saque', 'Sucesso de Passe']

    # Get the dataframe countries
    countries = (df["Team"].unique()).tolist()
    countries.sort()

    # Do a new dataframe with the sum of the metrics per country
    df_compare_countries = pd.DataFrame()
    df_compare_countries["Team"] = countries
    df_compare_countries = df[metrics].groupby("Team").sum()
    df_compare_countries["Team"] = countries

    # Colors for each subcategory
    colors = ["#003f5c", "#665191", "#a05195", "#d45087", "#f95d6a", "#ff7c43", "#ffa600"]

    # Get the categories
    categories = df_compare_countries.columns.to_list()[0:len(df_compare_countries.columns)-1] # Remove the last column (Team)

    # Create figure
    fig = go.Figure()

    # Initialize the bottom to zero
    bottom = np.zeros(len(countries))

    # Plotting the stacked bar chart
    for category_i in range(len(categories)): # Loop through each category
        y_axis = [] # Initialize the y_axis to an empty list
        for i in range(len(countries)): # Loop through each country to get the values for the current category
            y_axis.append(df_compare_countries[categories[category_i]][df_compare_countries["Team"] == countries[i]].values[0])
        # Add the bar trace
        fig.add_trace(go.Bar(
            x=countries,
            y=y_axis,
            name=name_categories[category_i],
            marker_color=colors[category_i]
        ))
        bottom += y_axis  # Update the bottom plus the current y_axis

    # Update the layout for stacked bars
    fig.update_layout(
        barmode='stack',
        title='Comparação de Países por Métricas',
        title_x=0.5,
        xaxis=dict(title='Países'),
        yaxis=dict(title='Quantidade de Sucessos')
    )

    # Add annotation text under the legend
    fig.add_annotation(
        text="*Sucesso: Desencadeou ou Impediu ponto",
        xref="paper", yref="paper",
        x=1.5, y=0.53,
        showarrow=False,
        font=dict(size=12)
    )

    return fig

# Callback to update the scatter chart based on the selected genre
@app.callback(
    Output("scatter_chart", "figure"),
    Input("generos-radio", "value")
)
def generate_scatter_chart(selected_genero):
    df, _ = return_df_genero(selected_genero)
    df = df[
    (df['Points-attacks'] > 0) |
    (df["Succesful-receive"] > 0) |
    (df["Successful-setter"] > 0)]

    # Create figure
    markers = ['circle', 'triangle-up', 'star', 'triangle-down', 'square', 'x', 'diamond']
    
    fig = go.Figure()

    # Ataques
    fig.add_trace(go.Scatter(
        x=df['Attempts-shots-attack'],
        y=df['Points-attacks'],
        mode='markers',
        name='Ataques',
        marker=dict(symbol=markers[0], size=8, color='blue', line=dict(width=2, color='black'))
    ))

    # Recepções
    fig.add_trace(go.Scatter(
        x=df['Attemps-receive'],
        y=df['Succesful-receive'],
        mode='markers',
        name='Recepções',
        marker=dict(symbol=markers[1], size=8, color='green', line=dict(width=2, color='black'))
    ))

    # Levantamentos
    fig.add_trace(go.Scatter(
        x=df['Attempts-setter'],
        y=df['Successful-setter'],
        mode='markers',
        name='Levantamentos',
        marker=dict(symbol=markers[5], size=8, color='red', line=dict(width=1, color='black'))
    ))

    # Update layout
    fig.update_layout(
        title='Correlação entre Tentativas e Sucessos de todos os Países',
        title_x=0.5,
        xaxis_title='Número de Tentativas',
        yaxis_title='Número de Sucessos',
        legend_title='Categorias',
        template='plotly_white'
    )

    return fig

# Callback to update the options of the country dropdown based on the selected genre
@app.callback(
    Output('country', 'options'),
    Input('generos-radio', 'value'))

# Function to update the options of the country dropdown based on the selected genre
def set_country_options(selected_genero):
    df, _ = return_df_genero(selected_genero)

    df = df.sort_values(by="Team") # Sorting the dataframe by the column "Team" (Alphabetical order)
    # Creating the options for the dropdown based on the unique values of the column "Team"
    country_options = [{'label': country, 'value': country} for country in df['Team'].unique()]

    return country_options

# Callback to update the value of the country dropdown
@app.callback(
    Output('country', 'value'),
    Input('country', 'options'))
def set_country_value(available_options):
    return available_options[0]['value'] if available_options else None

# Callback to update the pie chart based on the selected country
@app.callback(
    Output("pie_chart", "figure"),
    Input("country", "value"),
    Input("generos-radio", "value")
)
def generate_pie_chart(country, selected_genero):
    if not country:
        return go.Figure()
    df, _ = return_df_genero(selected_genero)

    df = df[(df['Team'] == country)]

    labels = ['Ataque', 'Bloqueio', 'Saque']
    sizes = [
        df['Attack-Points'].sum(),
        df['Block-Points'].sum(),
        df['Serve-Points'].sum()
    ]

    fig = px.pie(values=sizes, names=labels, hole=0.3)
    # Update the traces to change the colors of the percentage numbers and add white lines between divisions
    fig.update_traces(
        textinfo='percent',
        textfont=dict(color='white'),  # Change the color and size of the percentage numbers
        marker=dict(
            line=dict(color='white', width=3)  # Add white lines between the divisions
        )
    )

    # Update the layout
    fig.update_layout(
        showlegend=True,
        title = "Distribuição de Pontos por Categoria de um País",
        title_x=0.5
    )
    
    return fig

# Callback to update the scatter chart of attack X block based on the selected genre and team
@app.callback(
    Output("scatter_chart_attacks_blocks", "figure"),
    Input("generos-radio", "value"),
    Input("country", "value")
)
def generate_scatter_attacks_blocks(selected_genero, selected_country):
    fig = go.Figure()

    return fig

# Callback to update the options of the player dropdown based on the selected genre and country
@app.callback(
    Output('player', 'options'),
    Input('generos-radio', 'value'),
    Input('country', 'value')
)
# Function to update the options of the player dropdown based on the selected genre and country
def set_players_options(selected_genero, selected_country):
    df, _ = return_df_genero(selected_genero)

    df = df.sort_values(by="Player-Name") # Sorting the dataframe by the column "Player-Name" (Alphabetical order)
    # Creating the options for the dropdown based on the unique values of the column "Player-Name"
    player_options = [{'label': i, 'value': i} for i in df[df["Team"] == selected_country]["Player-Name"].unique()]

    return player_options

# Callback to update the value of the player dropdown
@app.callback(
    Output('player', 'value'),
    Input('player', 'options'))
def set_player_value(available_options):
    return available_options[0]['value'] if available_options else None

# Callback to update the player statistics based on the selected player
@app.callback(
    Output("players_chart", "figure"),
    Input("player", "value"),
    Input("generos-radio", "value")
)
def generate_player_statistics(player, selected_genero):
    if not player:
        return go.Figure()

    df, color = return_df_genero(selected_genero)
    player_data = df[df['Player-Name'] == player]

    # Metrics to be displayed in the polar chart
    metrics = ['Attack-Points', 'Block-Points', 'Total-dig', 'Total-receive', 'Serve-Points', 'Total-setter']
    # metrics = ['Success-percent-attack', 'Efficiency-percent-block', 'Success-percent-dig', 'Success-percent-receive', 'Success-percent-serve', 'Success-percent-setter']
    # metrics = ['Points-attacks', 'Succesful-blocks', 'Successful-dig', 'Succesful-receive','serve-points', 'Successful-setter']

    fig = go.Figure() # Create a new figure

    # Add the player data to the polar chart
    for i, (idx, row) in enumerate(player_data.iterrows()):
        fig.add_trace(go.Scatterpolar(
            r=row[metrics].values,
            theta=['Ataque', 'Bloqueio', 'Defesa', 'Defesa de Saque', 'Saque', 'Levantar/Setter'],
            fill='toself',
            name=f"{row['Player-Name']} ({row['Team']})",
            marker=dict(
                size=10
            ),
            line=dict(
                width=3,
                color=color[i]
            )
        ))

    # Update the polar chart
    fig.update_polars(
        angularaxis=dict(
            rotation=0,
            direction="clockwise",
            showline=True,
            linecolor="black",
            showticklabels=True,
            ticks="outside",
            tickwidth=1,
            ticklen=1,
            tickcolor="black",
            tickfont=dict(
                family="Arial",
                size=20,
                color="black"
            ),
            showgrid=True
        ),
        radialaxis=dict(
            showline=True,
            range=[0, player_data[metrics].max().max()*1.1],
            showticklabels=False
        )
    )
    # Update the layout
    fig.update_layout(
        showlegend=False,
        title = "Estatísticas do Jogador",
        title_x=0.5
    )
    
    return fig

if __name__ == '__main__':
    app.run(debug=True)