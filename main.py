import streamlit as st
import pandas as pd
import plotly.express as px
import altair as alt
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
from PIL import Image

# Titre de l'application
st.title('Population, Housing and Social Housing in France')
# Problématique
st.markdown ("How do demographics, housing characteristics and social housing policies interact to influence the well-being of residents in a given region?")

# Fonction pour charger les données depuis mon fichier CSV local
@st.cache_data
def load_data(nrows):
    # Définition du nom des colonnes
    column_names = [
        "annee_publication", "code_departement", "nom_departement", "code_region", "nom_region",
        "nombre_d_habitants", "densite_de_population_au_km2", "variation_de_la_population_sur_10_ans_en",
        "dont_contribution_du_solde_naturel_en", "dont_contribution_du_solde_migratoire_en",
        "population_de_moins_de_20_ans", "population_de_60_ans_et_plus", "taux_de_chomage_au_t4_en",
        "taux_de_pauvrete_en", "nombre_de_logements", "nombre_de_residences_principales",
        "taux_de_logements_sociaux_en", "taux_de_logements_vacants_en", "taux_de_logements_individuels_en",
        "moyenne_annuelle_de_la_construction_neuve_sur_10_ans_en", "construction", "parc_social_nombre_de_logements",
        "parc_social_logements_mis_en_location", "parc_social_logements_demolis",
        "parc_social_ventes_a_des_personnes_physiques", "parc_social_taux_de_logements_vacants_en",
        "parc_social_taux_de_logements_individuels_en", "parc_social_loyer_moyen_en_eur_m2_mois",
        "parc_social_age_moyen_du_parc_en_annees", "parc_social_taux_de_logements_energivores_e_f_g_en",
        "geom", "geo_point_2d"
    ]

# Charger les données en spécifiant le séparateur (;) et les noms de colonnes et les colonne skip car pas normal
    data = pd.read_csv('logements-et-logements-sociaux-dans-les-departements.csv', sep=';', nrows=nrows, skiprows=[0, 2, 8], names=column_names)

    return data


with st.sidebar:
    image = Image.open('log france.jpg')
    st.image(image)
    st.write("My link :")
    st.write("[Github](https://github.com/stve-the-sheep)")
    st.write("[Linkedin](https://www.linkedin.com/in/steve-itte-9a67041b7/)")

# Affichage d'un texte pour informer l'utilisateur que les données se chargent
data_load_state = st.text('Loading data...')

# Charger les données depuis le fichier local en utilisant la fonction load_data
data = load_data(10000)

# Création d'une ligne horizontale pour choisir l'année
selected_year = st.slider("Select a year", 2018, 2022)

with st.expander("Explanation"):
    st.write("""
    With this line, you can select the year of your choice on certain graphs, enabling you to obtain the specific data for that particular year.""")
# Filtrer les données en fonction de l'année sélectionnée
filtered_data = data[data['annee_publication'] == selected_year]

# Création d'une nouvelle colonne population_entre_20_et_60

filtered_data['population_entre_20_et_60'] = filtered_data['population_de_60_ans_et_plus']- filtered_data['population_de_moins_de_20_ans']

# Création une case déroulante pour choisir la partie que vous souhaitez
selected_chart_section = st.selectbox("Select a section", ["Introduction", "Population", "Housing", "Social housing", "Conclusion"])

# ##############################################################################

# Introduction
if selected_chart_section == "Introduction":
    st.subheader("Introduction")
    
    # Création d'une case déroulante pour choisir la sous partie
    selected_chart_type = st.selectbox("Select sub-sections",["Population frequency", "Map of France", "Population representation", "Correlation matrix"])

# #######################################

# Histogramme 1

    if selected_chart_type == "Population frequency":
        st.subheader('Histogram of the number of inhabitants')
        chart = alt.Chart(filtered_data).mark_bar().encode(
            alt.X('nombre_d_habitants:Q', bin=True),
            alt.Y('count():Q', title='Fréquence')
        ).properties(width=500)
        st.altair_chart(chart)
        
        
        with st.expander("Explanation"):
            st.write("""
                     We present the distribution of cities according to the number of inhabitants, classified in intervals ranging from 0 to 500,000, from 500,000 to 1 million, and so on...
                     """)
        
        # Sélection de la région
        selected_region = st.selectbox("Select a region", data['nom_region'].unique())

        # Filtrer les données en fonction de la région sélectionnée
        filtered_data = data[data['nom_region'] == selected_region]

        # Sélection de la colonne à afficher dans l'histogramme
        selected_column = st.selectbox("Select a column", data.columns)

        # Créer l'histogramme
        fig = px.histogram(filtered_data, x=selected_column, title=f'Histogramme of {selected_column} for {selected_region}')

        # Personnaliser l'axe des x
        fig.update_xaxes(title=selected_column)

        # Personnaliser l'axe des y
        fig.update_yaxes(title='Frequency')

        # Afficher l'histogramme
        st.plotly_chart(fig)
        
        
        with st.expander("Explanation"):
            st.write("""
            You have the power of total customisation! Choose the region you're interested in and select the column of data you want to explore. Explore the data at your leisure for a personalised experience.
            """)
        
# #######################################

    elif selected_chart_type == "Map of France":
        
# Code pour afficher une carte Plotly Express en utilisant la colonne "geo_point_2d"
        st.subheader('Map of geographical coordinates')
        fig = px.scatter_mapbox(filtered_data, 
                            lat=filtered_data['geo_point_2d'].str.split(',').str[0].astype(float),
                            lon=filtered_data['geo_point_2d'].str.split(',').str[1].astype(float),
                            hover_name="nom_departement", hover_data=["nombre_d_habitants"],
                            title="Map of geographical coordinates",
                            zoom=5)
        fig.update_layout(mapbox_style="carto-positron")
        fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
        st.plotly_chart(fig)
        
        
        with st.expander("Explanation"):
            st.write("""
                An interactive map of France, including the overseas regions (DROM-TOM), showing the population distribution by region. You can select the reference year using the scroll bar above.
                     """)
            
# #######################################

    elif selected_chart_type == "Population representation":
        
# Camembert 1
        # Création d'un camembert des régions avec le plus d'habitants
        st.subheader('Pie chart of the regions with the most inhabitants')
        sorted_data = filtered_data.sort_values(by='nombre_d_habitants', ascending=False)
        top_regions = sorted_data[~sorted_data['code_departement'].str.startswith('VILLE')]

        fig3 = px.pie(top_regions, names='nom_region', values='nombre_d_habitants',
                      title='Breakdown of population by region')
        st.plotly_chart(fig3)
        
        
        with st.expander("Explanation"):
            st.write("""
                We list the regions with the largest total population. At the top of the list is Île-de-France, closely followed by Auvergne-Rhône-Alpes and Hauts-de-France.
                     """)
        
# Camembert 2
        # Création d'un camembert de la population de 60 ans et plus par région
        st.subheader(f'Pie chart of the population aged 60 and over by region ({selected_year})')
        fig2 = px.pie(filtered_data, names='nom_region', values='population_de_60_ans_et_plus',
                      title=f'Population aged 60 and over by region ({selected_year})')
        st.plotly_chart(fig2)
        
        
        with st.expander("Explanation"):
            st.write("""
              We identify the regions with the largest populations aged 60 and over. Occitanie is in first place, closely followed by Nouvelle-Aquitaine and Auvergne-Rhône-Alpes.
                     """)
# Camembert 3
        # Création d'un camembert de la population de moins de 20 ans par région
        st.subheader(f'Pie chart of population under 20 by region ({selected_year})')
        fig1 = px.pie(filtered_data, names='nom_region', values='population_de_moins_de_20_ans',
                      title=f'Population under 20 by region ({selected_year})')
        st.plotly_chart(fig1)
        
        
        with st.expander("Explanation"):
            st.write("""
               We list the regions with the largest under-20 populations. In first place is Occitanie, closely followed by Auvergne-Rhône-Alpes and Nouvelle-Aquitaine.
                     """)
# Camembert 4 
        # Création d'un camembert de la population entre 20 et 60 ans
        st.subheader (f'Pie chart of the population aged between 20 and 60 by region({selected_year})')
        fig4 = px.pie(filtered_data, names='nom_region', values = 'population_entre_20_et_60',
                      title=f'Population aged between 20 and 60 by region({selected_year})')
        st.plotly_chart(fig4)
        
        
        with st.expander("Explanation"):
            st.write("""
               We look at the regions with the largest populations aged between 20 and 60. At the top of the list is Occitanie, closely followed by Bourgogne-Franche-Comté and Auvergne-Rhône-Alpes.
                     """)
# #######################################

    elif selected_chart_type == "Correlation matrix":
        
        # Sélection uniquement des colonnes numériques
        numeric_columns = [
            "nombre_d_habitants", "densite_de_population_au_km2", "variation_de_la_population_sur_10_ans_en",
            "dont_contribution_du_solde_naturel_en", "dont_contribution_du_solde_migratoire_en",
            "population_de_moins_de_20_ans", "population_de_60_ans_et_plus", "taux_de_chomage_au_t4_en",
            "taux_de_pauvrete_en", "nombre_de_logements", "nombre_de_residences_principales",
            "taux_de_logements_sociaux_en", "taux_de_logements_vacants_en", "taux_de_logements_individuels_en",
            "moyenne_annuelle_de_la_construction_neuve_sur_10_ans_en", "construction", "parc_social_nombre_de_logements",
            "parc_social_logements_mis_en_location", "parc_social_logements_demolis",
            "parc_social_ventes_a_des_personnes_physiques", "parc_social_taux_de_logements_vacants_en",
            "parc_social_taux_de_logements_individuels_en", "parc_social_loyer_moyen_en_eur_m2_mois",
            "parc_social_age_moyen_du_parc_en_annees", "parc_social_taux_de_logements_energivores_e_f_g_en"
        ]

        # Création la matrice de corrélation
        correlation_matrix = data[numeric_columns].corr()

        # Définissions la taille de la figure
        plt.figure(figsize=(15, 12))

        # Visualisation la matrice de corrélation
        plt.figure(figsize=(12, 10))
        sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', linewidths=0.5)
        plt.title('Correlation matrix')
        st.pyplot(plt)
        
        
        with st.expander("Explanation"):
            st.write("""
                The correlation matrix highlights the strongest relationships between the variables. The more red the colour, the more positive the correlation, while the more blue the colour, the more negative the correlation.
                     """)
# ##############################################################################

# Partie 1
elif selected_chart_section == "Population":
    st.subheader("Population")

    # Création d'une case pour choisir la sous partie
    selected_chart_type = st.selectbox("Select a type of graph", ["Population map", "Unemployment rate and social housing by region", "Population growth factors", "Population change and new construction", "The influence of population on parameters"])

# #######################################

    if selected_chart_type == "Population growth factors":
        # Facteurs de croissance de la population
        st.subheader("Population growth factors")

        # Sélection des colonnes pertinentes pour les facteurs de croissance
        growth_factors_data = filtered_data[["nom_region", "dont_contribution_du_solde_naturel_en", "dont_contribution_du_solde_migratoire_en"]]

        # Renommer les colonnes pour des noms plus conviviaux
        growth_factors_data.columns = ["Région", "Solde Naturel", "Solde Migratoire"]

        # Regrouper les données par région
        grouped_growth_factors_data = growth_factors_data.groupby("Région").sum().reset_index()

        # Création d'un graphique à barres empilées pour illustrer les contributions
        fig_growth_factors = px.bar(grouped_growth_factors_data, x="Région", y=["Solde Naturel", "Solde Migratoire"],
                                    labels={"Région": "Nom de la Région"}, title="Contributions au Solde Naturel et au Solde Migratoire",
                                    barmode='group')  # Utilisation de barmode='group' pour afficher deux histogrammes côte à côte

        
        # Affichage du graphique
        st.plotly_chart(fig_growth_factors)
        with st.expander("Explanation"):
            st.write("""
                We want to understand the factors behind population growth. The natural balance, which is the difference between the number of births and deaths recorded over a period, and apparent net migration, which is the difference between the number of people entering a given territory and the number leaving it over a period, help us to explore these aspects.

Let's take the example of Occitanie in 2018: we see a significant migratory balance, while the natural balance is in negative territory. This suggests that there was population movement among both local residents and migrants to Occitanie that year.
                     """)  
# #######################################

    elif selected_chart_type == "The influence of population on parameters":
        st.subheader('Nuage de points')
        # Nuage de points
        # Graphique de dispersion entre "nombre_de_residences_principales" et "nombre_d_habitants"
        fig = px.scatter(
            data,
            x='nombre_de_residences_principales',
            y='nombre_d_habitants',
            color='nom_region',  # Couleur par région
            labels={'nombre_de_residences_principales': 'Nombre de Résidences Principales', 'nombre_d_habitants': 'Nombre d\'Habitants'},
            title='Relationship between the number of main residences and the number of inhabitants'
        )
        # Afficher le graphique
        st.plotly_chart(fig)
        
        
        with st.expander("Explanation"):
            st.write("""
                Our objective is to analyse whether the number of principal residences has an impact on the number of inhabitants. We find that the influence of one on the other is very significant. In other words, the more inhabitants there are, whatever the year, the more principal residences there are.
                     """)
            
        fig1 = px.scatter(data, x="nombre_d_habitants", y="taux_de_chomage_au_t4_en", title="Scatter plot Population vs Unemployment rate")
        st.plotly_chart(fig1)
        
        
        with st.expander("Explanation"):
            st.write("""
                Our graph aims to determine whether the unemployment rate is affected by the number of inhabitants. It is notable that, whatever the size of the population, the unemployment rate seems to plateau at around 10%. This observation does not suggest a very strong correlation between the number of inhabitants and the unemployment rate.
                     """)
        
        # Graphique de dispersion : Densité de population vs Taux de chômage
        st.subheader('Scatter plot: Population density vs Unemployment rate')
        fig1 = px.scatter(data, x="densite_de_population_au_km2", y="taux_de_chomage_au_t4_en", title="Population density vs Unemployment rate")
        st.plotly_chart(fig1)
        
        
        with st.expander("Explanation"):
            st.write("""
                Our graph allows us to assess the mutual influence between population density per square kilometre and the unemployment rate. However, it is clear that these two variables do not appear to be mutually influenced, because even when the population density is close to zero, the unemployment rate remains high. It is interesting to note that the points on the right represent the major cities in France, such as Paris, Lyon, Bordeaux, and so on.
                     """)
            
        # Graphique de dispersion : Densité de population vs Taux de pauvreté
        st.subheader('Graphique de dispersion : Densité de population vs Taux de pauvreté')
        fig2 = px.scatter(data, x="densite_de_population_au_km2", y="taux_de_pauvrete_en", title="Population density vs poverty rate")
        st.plotly_chart(fig2)
        
        
        with st.expander("Explanation"):
            st.write("""
                Our graph allows us to analyse the influence between population density per square kilometre and the poverty rate. However, it is clear that these two variables do not seem to have a mutual influence, because even when population density is low, the poverty rate can vary. It is important to note that the points to the right of the graph represent the major cities in France, such as Paris, Lyon, Bordeaux and others.
                     """)
        
# #######################################

    elif selected_chart_type == "Population map":

# MAP 3
        # Remplace les valeurs NaN par 0 dans la colonne "nombre_de_residences_principales"
        data['nombre_de_residences_principales'].fillna(0, inplace=True)

        # Créer une carte Plotly Express avec les caractéristiques sélectionnées
        selected_columns = ["nombre_d_habitants", "densite_de_population_au_km2", "variation_de_la_population_sur_10_ans_en",
                            "dont_contribution_du_solde_naturel_en", "dont_contribution_du_solde_migratoire_en",
                            "population_de_moins_de_20_ans", "population_de_60_ans_et_plus",
                            "taux_de_chomage_au_t4_en", "taux_de_pauvrete_en"]

        fig = px.scatter_geo(
            data,
            lat=data['geo_point_2d'].str.split(',').str[0].astype(float),
            lon=data['geo_point_2d'].str.split(',').str[1].astype(float),
            color='nombre_d_habitants',
            hover_name='nom_departement',
            hover_data=selected_columns,
            title='Selected Data Map',
            color_continuous_scale='Viridis',  # Palette de couleurs
            size_max=25,  # Taille max des marqueurs
        )

        fig.update_geos(
            center=dict(lat=46.603354, lon=1.888334),  
            # Centre de la carte (coordonnées de la France)
            projection_scale=5.5,  # Zoom
        )
        st.plotly_chart(fig)
        
        
        with st.expander("Explanation"):
            st.write("""
                An interactive map of the population of the regions, based on several key indicators such as the number of inhabitants, the population density per square kilometre, the change in population over a decade, the contribution of the natural and migratory balances, the population aged under 20, the population aged 60 and over, the unemployment rate in the fourth quarter and the poverty rate.
                     """)
            
# #######################################
        
    elif selected_chart_type == "Population change and new construction":
        st.subheader('Line graph')
                
# Ligne 1
        selected_location = st.selectbox("Select a location", data["nom_departement"].unique())
        filtered_data = data[data["nom_departement"] == selected_location]

        st.subheader(f"Variation of the population for {selected_location}")
        chart1 = alt.Chart(filtered_data).mark_line().encode(
            x="annee_publication:T",
            y="variation_de_la_population_sur_10_ans_en:Q",
            tooltip=["annee_publication:T", "variation_de_la_population_sur_10_ans_en:Q"]
        ).properties(width=600, height=300)
        st.altair_chart(chart1)

# Ligne 2
        st.subheader(f"Average annual new build for {selected_location}")
        chart2 = alt.Chart(filtered_data).mark_line().encode(
            x="annee_publication:T",
            y="moyenne_annuelle_de_la_construction_neuve_sur_10_ans_en:Q",
            tooltip=["annee_publication:T", "moyenne_annuelle_de_la_construction_neuve_sur_10_ans_en:Q"]
        ).properties(width=600, height=300)

        st.altair_chart(chart2)
        
        
        with st.expander("Explanation"):
            st.write("""
                We look at the change in population over a decade and the annual average of new construction over the same period.

Let's take the Côte-d'Or as an example: although the population is tending to fall, this is not preventing the construction of new infrastructure. This observation suggests that population change does not have a significant influence on new housing construction.
                     """)
# #######################################
                
    elif selected_chart_type == "Unemployment rate and social housing by region":
        st.subheader('pie')
        
        selected_location = "Régions"
        selected_feature = st.selectbox("Select a feature", ["taux_de_chomage_au_t4_en", "taux_de_logements_sociaux_en"])
        pie_data = filtered_data.groupby("nom_region")[selected_feature].mean().reset_index()
        pie_data = pie_data.rename(columns={selected_feature: "Pourcentage"})
        total_percentage = pie_data["Pourcentage"].sum()
        pie_data["Pourcentage"] = pie_data["Pourcentage"] / total_percentage
        pie_chart = alt.Chart(pie_data).mark_arc().encode(
            theta="Pourcentage:Q",
            color="nom_region:N",
            tooltip=["nom_region:N", "Pourcentage:Q"]
        ).properties(
            width=700,
            height=500,
            title=f"Repartition of {selected_feature} for {selected_location}"
        ).configure_legend(title=None)
        
        st.altair_chart(pie_chart)

        
        with st.expander("Explanation"):
            st.write("""
                You can choose between two graphs. The first shows the unemployment rate by region, with the highest rates in the French overseas departments and territories (DROM-TOM). The second graph shows the rate of social housing, with Île-de-France in the lead, followed by the DROM-TOM.

It is interesting to note an initial correlation between the unemployment rate and the social housing rate. When the population has a high unemployment rate, the rate of social housing tends to increase. However, this relationship is relatively weak, as Île-de-France has one of the lowest unemployment rates, while having one of the highest social housing rates.
                     """)
        
# ##############################################################################

# Partie 2
elif selected_chart_section == "Housing":
    st.subheader("Housing")

    # Créer une case à cocher pour choisir la sous partie 
    selected_chart_type = st.selectbox("Select a type of graph", ["Housing Statistics", "Geographical Distribution", "Relation to Population"])

# #######################################
    
    if selected_chart_type == "Housing Statistics":

#Histogramme
        # Sélection d'une région
        selected_region = st.selectbox("Select a region", data['nom_region'].unique())

        # Filtrer les données en fonction de la région sélectionnée
        filtered_data = data[data['nom_region'] == selected_region]

        # Création d'une ligne choisir les années
        selected_years = st.slider("Select a year range", 2018, 2022, (2018, 2022))

        # Filtrer les données en fonction de la plage d'années sélectionnée
        filtered_data = filtered_data[(filtered_data['annee_publication'] >= selected_years[0]) & (filtered_data['annee_publication'] <= selected_years[1])]

        # Création d'un DataFrame avec les valeurs de nombre_de_logements et nombre_de_residences_principales pour chaque année
        fig = px.bar(filtered_data, x='annee_publication', y=['nombre_de_logements', 'nombre_de_residences_principales'],
                     barmode='group', title=f'Number of dwellings and main residences ({selected_region})')

        # Personnalisation de l'axe des x
        fig.update_xaxes(categoryorder='total ascending', title='Année de Publication')

        # Personnalisation de l'axe des y
        fig.update_yaxes(title='Nombre')

        # Afficher le graphique
        st.plotly_chart(fig)
        

        with st.expander("Explanation"):
            st.write("""
                For the region of your choice, you can explore the number of dwellings in relation to the number of main residences. The remaining dwellings are either vacant or social housing. This gives you a complete overview of the distribution of housing in the selected region from 2018 to 2022.
                     """)
####################

# Camembert

        # Sélection des colonnes pour le camembert
        selected_columns = ["taux_de_logements_sociaux_en", "taux_de_logements_vacants_en", "taux_de_logements_individuels_en"]
        labels = ["Taux de Logements Sociaux", "Taux de Logements Vacants", "Taux de Logements Individuels"]
        values = filtered_data[selected_columns].mean().values.tolist()

        # Créer un graphique camembert comparant les taux
        fig = px.pie(names=labels, values=values, title=f"Comparison of housing rates ({selected_year})")
        fig.update_traces(textinfo='percent+label', pull=[0.1, 0.1, 0.1])

        # Afficher le camembert
        st.plotly_chart(fig)

        
        with st.expander("Explanation"):
            st.write("""
                For the selected region, you can obtain information on the rate of individual, social and vacant dwellings. You can select the year using the horizontal bar.
                     """)
# #######################################

    elif selected_chart_type == "Geographical Distribution":
        
# MAP 2
        # Code pour afficher une carte Plotly Express avec toutes les caractéristiques sélectionnées
        selected_columns = ["nombre_de_logements", "nombre_de_residences_principales",
                            "taux_de_logements_sociaux_en", "taux_de_logements_vacants_en",
                            "taux_de_logements_individuels_en"]
        map_data = filtered_data[selected_columns]
        map_data["Latitude"] = filtered_data['geo_point_2d'].str.split(',').str[0].astype(float)
        map_data["Longitude"] = filtered_data['geo_point_2d'].str.split(',').str[1].astype(float)
        for col in selected_columns:
            map_data[col] = pd.to_numeric(map_data[col])
        fig = px.scatter_mapbox(map_data,
                                lat="Latitude",
                                lon="Longitude",
                                color="nombre_de_logements",
                                size="nombre_de_residences_principales",
                                hover_data=["taux_de_logements_sociaux_en", "taux_de_logements_vacants_en", "taux_de_logements_individuels_en"],
                                title="Carte des Données Sélectionnées",
                                zoom=5)
        fig.update_layout(mapbox_style="carto-positron")
        fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
        st.plotly_chart(fig)


        with st.expander("Explanation"):
            st.write("""
                On this map of France, we present several indicators, including the number of dwellings, the rate of social housing, the rate of vacant dwellings, the rate of detached dwellings and the number of main residences.

It is interesting to note that France's major cities, such as Paris, Marseille, Lyon, Bordeaux and others, are represented by the largest circles and have the highest numbers of homes. This reflects the importance of urban areas in terms of housing in the country.
                     """)
# #######################################

    elif selected_chart_type == "Relation to Population":
        
        filtered_data = data[data['annee_publication'] == selected_year]
        # Création d'un nuage de points en fonction de l'année sélectionnée
        
        scatter_fig = px.scatter(filtered_data, x='nombre_d_habitants', y='nombre_de_logements',
                                 labels={'nombre_d_habitants': 'Nombre d\'Habitants', 'nombre_de_logements': 'Nombre de Logements'},
                                 title=f'Scatter plot: Number of inhabitants vs. number of dwellings ({selected_year})')
        # Affichage du nuage de points
        st.plotly_chart(scatter_fig)

        
        with st.expander("Explanation"):
            st.write("""
                We can see that the number of inhabitants closely follows the number of homes. In other words, the more inhabitants there are, the more homes are available. These two parameters are very strongly correlated, suggesting a relationship between the population and the number of available homes.
                     """)
# ###############
        
        scatter_fig = px.scatter(filtered_data, x='taux_de_pauvrete_en', y=['taux_de_logements_sociaux_en', 'taux_de_logements_vacants_en', 'taux_de_logements_individuels_en'],
                         labels={'taux_de_pauvrete_en': 'Taux de Pauvreté', 'value': 'Taux'},
                         title=f'Relationship between Poverty Rates and Housing Rates ({selected_year})')

        # Ajout d'une légende
        scatter_fig.update_traces(marker=dict(size=12),
                                  selector=dict(mode='markers+text'),
                                  text=['Logements Sociaux', 'Logements Vacants', 'Logements Individuels'])
        st.plotly_chart(scatter_fig)

        
        with st.expander("Explanation"):
            st.write("""
                We examine whether the poverty rate has an impact on different housing rates. It is clear that when the poverty rate is between 10% and 23%, this favours an increase in housing rates, whether social, vacant or detached. In other words, the less the population is affected by poverty, the more housing is available, whatever its nature.
                     """)
            
# ###############
        with st.container():
            st.subheader("New Build vs Population Under 20")
            fig1 = px.scatter(filtered_data, x='moyenne_annuelle_de_la_construction_neuve_sur_10_ans_en', y='population_de_moins_de_20_ans',
                              labels={'moyenne_annuelle_de_la_construction_neuve_sur_10_ans_en': 'Construction Neuve Moyenne (10 ans)',
                                      'population_de_moins_de_20_ans': 'Moins de 20 ans'},
                              title=f'New Build vs Population Under 20 ({selected_year})')
            st.plotly_chart(fig1)

            
        with st.expander("Explanation"):
            st.write("""
                Our objective is to analyse the potential influence of the under-20 population on new construction. The graph on the left shows the frequency of population under 20 in relation to new construction over a decade. It is notable that these two variables do not appear to have a significant influence on each other. In other words, there is no apparent correlation between the population under 20 and new construction.
                     """)
            
            
        with st.container():
            st.subheader("New build vs Population aged 60 and over")
            fig2 = px.scatter(filtered_data, x='moyenne_annuelle_de_la_construction_neuve_sur_10_ans_en', y='population_de_60_ans_et_plus',
                              labels={'moyenne_annuelle_de_la_construction_neuve_sur_10_ans_en': 'Construction Neuve Moyenne (10 ans)',
                                      'population_de_60_ans_et_plus': '60 ans et plus'},
                              title=f'New build vs Population aged 60 and over ({selected_year})')
            st.plotly_chart(fig2)


        with st.expander("Explanation"):
            st.write("""
                We are trying to determine whether the population over 60 has an influence on new construction. On the left, we have plotted the frequency of the over-60 population in relation to new construction over a ten-year period. The observation reveals not only the absence of influence, but also an inverse relationship, since the more people there are of this age, the less new construction there is. In other words, these two variables appear to be negatively correlated.
                     """)
            
            
# ###############
        selected_years = st.slider("Select a year range", 2018, 2022, (2018, 2022))

            # Filtrer les données en fonction de la plage d'années sélectionnée
        filtered_data = data[(data['annee_publication'] >= selected_years[0]) & (data['annee_publication'] <= selected_years[1])]

            # Sélection des variables pour les graphiques
        variables = ["nombre_d_habitants", "densite_de_population_au_km2", "construction"]

            # Créer le premier graphique
        st.subheader("Number of inhabitants vs. construction")
        fig1 = px.scatter(filtered_data, x="construction", y="nombre_d_habitants", title="Number of inhabitants vs. construction")
        st.plotly_chart(fig1)

            
        with st.expander("Explanation"):
            st.write("""
                This graph allows us to determine whether the number of inhabitants has an influence on construction. It is clear that the two variables are very strongly correlated, suggesting a significant relationship. In other words, the number of inhabitants seems to have a considerable influence on the level of construction.
                     """)
            
            
            # Créer le deuxième graphique
        st.subheader("Population density vs. construction")
        fig2 = px.scatter(filtered_data, x="construction", y="densite_de_population_au_km2", title="Population density vs. construction")
        st.plotly_chart(fig2)

            
        with st.expander("Explanation"):
            st.write("""
                This graph allows us to analyse the influence of population density per square kilometre on construction. We can see that, whatever the population density, the level of construction remains high. However, it is interesting to note that, contrary to intuition, a very high population density seems to be associated with less building, while a medium population density seems to favour more building. In short, the relationship between population density and construction is not linear, and moderate densities may stimulate more construction.
                     """)
# ##############################################################é

# Partie 3
elif selected_chart_section == "Social housing":
    st.subheader("Social housing")

    # Créer une case à cocher pour choisir le type de graphique
    selected_chart_type = st.selectbox("Select a chart type", ["Social Housing Statistics", "Impact on the Population", "Social Housing Policies"])

# #######################################

    if selected_chart_type == "Social Housing Statistics":
        
        selected_years = st.slider("Select a year range", 2018, 2022, (2018, 2022))
        # Filtrer les données en fonction de la plage d'années sélectionnée
        filtered_data = data[(data['annee_publication'] >= selected_years[0]) & (data['annee_publication'] <= selected_years[1])]

        # Variables à inclure dans l'histogramme
        variables = ["parc_social_nombre_de_logements", "parc_social_logements_mis_en_location", "parc_social_logements_demolis"]

        # Créer un histogramme pour les trois variables sur le même graphique
        hist_fig = px.histogram(filtered_data, x=variables, title="Histogram of Social Housing Parameters")
        hist_fig.update_layout(barmode='group')  # Superpose les histogrammes

        # Afficher le graphique
        st.plotly_chart(hist_fig)

        
        with st.expander("Explanation"):
            st.write("""
                We see that the number of social housing units demolished and the number of social housing units let are equal. Then we have the frequency of the total number of dwellings, and it appears that most of the social housing stock comprises between 5,000 and 10,000 dwellings.
                     """)
            
            
# ###################
        
        selected_region = st.selectbox("Select a region", data['nom_region'].unique())

        # Filtrer les données en fonction de la région sélectionnée
        filtered_data = data[data['nom_region'] == selected_region]

        fig = px.histogram(filtered_data, x='parc_social_age_moyen_du_parc_en_annees',
                           title=f"Histogram of the average age of the social housing stock for {selected_region}")

        fig.update_xaxes(title="Average age of social housing stock in years")

        fig.update_yaxes(title='Frequency')

        st.plotly_chart(fig)


        with st.expander("Explanation"):
            st.write("""
                We examine the frequency of the average age of social housing stock. For the Bourgogne-Franche-Comté region, the majority of social housing appears to have an average age of between 40 and 41 years.
                     """)
            
            
# #######################################

    elif selected_chart_type == "Impact on the Population":
        
        # Filtrer les données en fonction de la plage d'années sélectionnée
        selected_years = st.slider("Select a year range", 2018, 2022, (2018, 2022))
        filtered_data = data[(data['annee_publication'] >= selected_years[0]) & (data['annee_publication'] <= selected_years[1])]

        # Graphique de dispersion : Relation entre le nombre de logements sociaux et la densité de population
        scatter_fig = px.scatter(filtered_data, x='densite_de_population_au_km2', y='parc_social_nombre_de_logements', 
                                 labels={'densite_de_population_au_km2': 'Densité de Population au km2', 
                                         'parc_social_nombre_de_logements': 'Nombre de Logements Sociaux'},
                                 title='Relationship between social housing and population density')
        st.plotly_chart(scatter_fig)

        
        with st.expander("Explanation"):
            st.write("""
                This graph shows the relationship between social housing and population density. It is clear that the higher the population density, the more social housing there is. This observation suggests a positive correlation between these two variables, meaning that densely populated areas tend to have more social housing.
                     """)
            
            
        # Histogramme : Distribution des taux de logements sociaux
        histogram_fig = px.histogram(filtered_data, x='taux_de_logements_sociaux_en', nbins=20, 
                                     labels={'taux_de_logements_sociaux_en': 'Taux de Logements Sociaux', 
                                             'count': 'Nombre de Régions'},
                                     title='Distribution of social housing rates')
        st.plotly_chart(histogram_fig)

        
        with st.expander("Explanation"):
            st.write("""
                This graph gives us an overview of the distribution of social housing rates. In general, we can see that the social housing rate in a city is mainly between 7.5% and 9.49%. This range of values seems to represent the norm for the rate of social housing in the cities studied.
                     """)
            
            
        # Graphique à barres empilées : Répartition de la population par groupe d'âge
        age_groups = ['population_de_moins_de_20_ans', 'population_de_60_ans_et_plus']
        age_group_data = filtered_data[age_groups].sum()
        age_group_bar_fig = go.Figure(data=[
            go.Bar(x=age_group_data.index, y=age_group_data.values)
        ])
        age_group_bar_fig.update_layout(
            xaxis_title='Groupes d\'Âge',
            yaxis_title='Population',
            title='Breakdown of population by age group',
            barmode='stack'
        )
        st.plotly_chart(age_group_bar_fig)

        
        with st.expander("Explanation"):
            st.write("""
                Our objective is to determine which age group of the population most often occupies social housing. We found that the majority of people living in social housing are over 60.
                     """)
            
            
        # Graphique à barres : comparaison du nombre de logements sociaux par région
        bar_grouped_fig = px.bar(filtered_data, x='nom_region', y='parc_social_nombre_de_logements', 
                                 labels={'nom_region': 'Région', 'parc_social_nombre_de_logements': 'Nombre de Logements Sociaux'},
                                 title='Comparison of the number of social housing units by region')
        bar_grouped_fig.update_xaxes(tickangle=45)
        st.plotly_chart(bar_grouped_fig)

        with st.expander("Explanation"):
            st.write("""
                Our aim is to find out which region has the highest number of social housing units. Unsurprisingly, Île-de-France tops the list.
                     """)    
        
        # Corrélation entre le nombre de logements sociaux et d'autres paramètres
        correlation_matrix = filtered_data[['parc_social_nombre_de_logements', 'taux_de_chomage_au_t4_en', 'taux_de_pauvrete_en']].corr()
        heatmap_fig = go.Figure(data=go.Heatmap(z=correlation_matrix.values,
                                                x=correlation_matrix.columns,
                                                y=correlation_matrix.columns,
                                                colorscale='Viridis'))
        heatmap_fig.update_layout(title='Correlation matrix')
        st.plotly_chart(heatmap_fig)
        

        with st.expander("Explanation"):
            st.write("""
                The correlation matrix gives us an overview of the relationships between different variables. It is clear that poverty and unemployment are highly correlated, suggesting a mutual influence between these two factors. On the other hand, the number of social housing units does not show any significant correlation with other variables, indicating that it is relatively independent of the other factors studied.
                     """)
            
            
# #######################################

    elif selected_chart_type == "Social Housing Policies":
        # Filtrer les données en fonction de la plage d'années sélectionnée
        selected_years = st.slider("Select a year range", 2018, 2022, (2018, 2022))
        filtered_data = data[(data['annee_publication'] >= selected_years[0]) & (data['annee_publication'] <= selected_years[1])]

        # Sélection les variables d'intérêt
        variables = ["taux_de_logements_sociaux_en", "taux_de_logements_vacants_en", "parc_social_loyer_moyen_en_eur_m2_mois"]

        # Comparaison des taux de logements sociaux, des taux de logements vacants et du loyer moyen par région
        fig = px.bar(filtered_data, x='nom_region', y=variables, 
                     labels={'nom_region': 'Région'},
                     title='Comparison of Social Housing Indicators by Region',
                     barmode='group')
        fig.update_xaxes(tickangle=45)
        st.plotly_chart(fig)

        
        with st.expander("Explanation"):
            st.write("""
                In this last graph, our aim is to determine whether the rate of social housing, whether vacant or not, has an influence on prices (by taking into account the number of dwellings). One notable observation concerns the French overseas departments and territories, where we find a low level of social housing at very low prices. Occitanie stands out with the highest average rent, while Île-de-France has the highest proportion of social housing. What's more, Occitanie also has the highest rate of vacant homes among the regions studied.
                     """)
            
# ##############################################################################

# Conclusion
elif selected_chart_section == "Conclusion":
    
    st.write("Our detailed analysis of demographics, housing and employment in France from 2018 to 2022 reveals complex relationships and interesting trends. Here is a summary of the key points:")
    
# Point 1: Population and Housing
    st.subheader("1. Population and Housing")
    st.write("We observed a strong correlation between the number of inhabitants and the number of dwellings, indicating a close relationship between these two variables. The larger the population, the more dwellings there are.")

# Point 2: Unemployment rate and social housing
    st.subheader("2. unemployment rate and social housing")
    st.write("Although we have observed a trend towards higher unemployment rates in the overseas regions (DROM-TOM) and in Île-de-France, it is important to note that the unemployment rate does not seem to be strongly influenced by the number of social housing units. Île-de-France also stands out for its relatively low unemployment rate despite a high number of social housing units")

# Point 3: Population density and construction
    st.subheader("3. Population density and construction")
    st.write("Population density seems to have a significant influence on the level of construction. However, it is interesting to note that a very high population density is associated with less construction, while a moderate density seems to favour more construction.")

# Point 4: Poverty rates and housing
    st.subheader("4. Poverty rates and housing")
    st.write("We have observed that when the poverty rate is between 10% and 23%, this favours a higher rate of social housing. The less the population is affected by poverty, the more housing is available, whether social, vacant or individual.")

# Point 5: Population in Social Housing
    st.subheader("5. Population in social housing")
    st.write("With regard to social housing, we found that the over-60s are the most represented population in these dwellings, suggesting that these dwellings may be occupied more by older people.")

# Point 6: Regional distribution of social housing
    st.subheader("6. Regional distribution of social housing")
    st.write("Unsurprisingly, Île-de-France stands out as the region with the highest number of social housing units.")

# Point 7: Correlation Matrix
    st.subheader("7. Correlation matrix")
    st.write("The correlation matrix revealed some important relationships. For example, unemployment and poverty are highly correlated, indicating a mutual influence, while the number of social housing units does not show a significant correlation with other variables.")

# Point 8: Influence on House Prices
    st.subheader("8. Influence on house prices")
    st.write("Finally, we examined the influence of the social housing rate on prices, taking into account the number of dwellings. We observed marked differences between regions, notably higher average rents in Occitanie, a high rate of social housing in Île-de-France, and a high rate of vacant dwellings in Occitanie.")

# General conclusion
    st.subheader("General Conclusion")
    st.write("In conclusion, our analysis has enabled us to gain a better understanding of the complex relationships between population, housing, employment, poverty and social housing in different regions of France. These observations are essential for informing public policies and decisions on housing and economic development.")
