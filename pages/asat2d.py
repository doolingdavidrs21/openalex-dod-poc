import pandas as pd
import plotly.express as px
#import altair as alt
import plotly.graph_objects as go
import streamlit as st
from streamlit_plotly_events import plotly_events
import math
import plotly.io as pio
#pio.templates.default = "plotly"  
pio.templates.default = "plotly_dark"
# https://discuss.streamlit.io/t/streamlit-overrides-colours-of-plotly-chart/34943
st.set_page_config(layout='wide')

st.title("Example: Papers with at least one Author affiliated with one of these institutions:")
st.markdown("""
* [Nanjing University of Aeronautics and Astronautics 南京航空航天大学 latitude': 32.036007,
   'longitude': 118.813805](http://www.nuaa.edu.cn/)
* [Shenyang Aerospace University 沈阳航空航天大学 'latitude': 41.92633,
   'longitude': 123.404305](http://en.sau.edu.cn/)
* [China Aerospace Science and Industry Corporation (China) 中国航天科工集团 'latitude': 39.9227,
   'longitude': 116.30908](http://english.casic.cn/)
* [Zhengzhou University of Aeronautics 郑州航空工业管理学院 'latitude': 34.716457,
   'longitude': 113.64419](http://zua.edu.cn/main.html)
* [North China Institute of Science and Technology 华北科技学院 'latitude': 39.953175,
   'longitude': 116.8048](http://www.ncist.edu.cn/)
* [China Aerospace Science and Technology Corporation 中国航天科技集团 'latitude': 39.804134,
   'longitude': 116.41882]('http://english.spacechina.com/n16421/index.html)
* [North China Institute of Aerospace Engineering 'latitude': 39.526268,
   'longitude': 116.73137](http://www.nciae.edu.cn/default.html)
* [Space Engineering University 'latitude': 40.35555,
   'longitude': 116.65844](http://www.mod.gov.cn/services/2017-06/15/content_4783023.htm)
* [North China Research Institute of Electro-optics 'latitude': 39.984455,
   'longitude': 116.491936](http://www.ncrieo.com/)
""")

# add an st.map maybe, would be cool
st.write("Topic modeling")

@st.cache_data()
def load_centroids_asat():
    #dg = pd.read_csv("penguins.csv", engine="pyarrow")
  #  df = pd.read_json(df.to_json())
    dg = pd.read_pickle('asatcentroids2d.pkl.gz')
    return dg[dg.cluster != -1]

@st.cache_data()
def load_dftriple_asat():
    dg = pd.read_pickle('asatdftriple2d.pkl.gz')
    return dg

@st.cache_data()
def load_dfinfo_asat():
    dg = pd.read_pickle('asatdfinfo2d.pkl.gz')
    return dg[dg['cluster'] != -1]

@st.cache_data()
def load_dfgeo_asat():
    dg = pd.read_pickle('asatgeo.pkl')
    return dg


centroids = load_centroids_asat()
dftriple = load_dftriple_asat()
dfinfo = load_dfinfo_asat()
dfinfo['cluster_'] = dfinfo["cluster"].apply(str)
dfgeo = load_dfgeo_asat()

st.map(dfgeo)

@st.cache_data()
def get_fig_asat():
    fig_centroids = px.scatter(centroids,
                           x='x',y='y',
                    color_discrete_sequence=['pink'],
                          hover_data=['x','y',
                                      'wrapped_keywords',
                                      'wrapped_concepts','cluster'])
    fig_centroids.update_traces(marker=dict(size=12,
                              line=dict(width=.5,
                                        color='DarkSlateGrey')),
                  selector=dict(mode='markers'))
    fig_papers = px.scatter(dfinfo[dfinfo.cluster != -1],
                           x='x',y='y',
                    color='cluster_',
                        hover_data = ['title','cluster',
                                      'publication_date'])
                     #     hover_data=['title','x','y',
                     #                 'z','cluster','wrapped_author_list',
                     #                 'wrapped_affil_list',
                     #                 'wrapped_keywords'])
    fig_papers.update_traces(marker=dict(size=4,
                              line=dict(width=.5,
                                        color='DarkSlateGrey')),
                  selector=dict(mode='markers'))
    layout = go.Layout(
        autosize=True,
        width=1000,
        height=1000,

        #xaxis= go.layout.XAxis(linecolor = 'black',
         #                 linewidth = 1,
         #                 mirror = True),

        #yaxis= go.layout.YAxis(linecolor = 'black',
         #                 linewidth = 1,
         #                 mirror = True),

        margin=go.layout.Margin(
            l=10,
            r=10,
            b=10,
            t=10,
            pad = 4
            )
        )

    fig3 = go.Figure(data=fig_papers.data + fig_centroids.data)
    fig3.update_layout(height=700)

                   # layout=layout)  
    return fig3


#centroids = load_centroids()
#dftriple = load_dftriple()
#dfinfo = load_dfinfo()
#dfinfo['cluster_'] = dfinfo["cluster"].apply(str)
bigfig = get_fig_asat()

st.subheader("Papers and Topics")
st.write("Use the navigation tools in the mode bar to pan and zoom. Papers are automatically clustered into subtopics. Topics are the bigger pink dots with representative keywords and phrases available on hover. Clicking on a topic or paper then triggers a report of the most profilic countries, affiliations, and authors associated with that topic.")
selected_point = plotly_events(bigfig, click_event=True, override_height=700)
if len(selected_point) == 0:
    st.stop()
    
#st.write(selected_point)

selected_x_value = selected_point[0]["x"]
selected_y_value = selected_point[0]["y"]
#selected_species = selected_point[0]["species"]

try:
    df_selected = dfinfo[
        (dfinfo["x"] == selected_x_value)
        & (dfinfo["y"] == selected_y_value)
    ]

#def make_clickable(url, name):
#    return '<a href="{}" rel="noopener noreferrer" target="_blank">{}</a>'.format(url,name)

#df_selected['link'] = df_selected.apply(lambda x: make_clickable(x['id'], x['id']), axis=1)
    st.data_editor(
        df_selected[['x', 'y', 'id', 'title', 'doi', 'cluster', 'probability',
       'publication_date', 'keywords', 'top_concepts', 'affil_list',
       'author_list']],
        column_config={
            "doi": st.column_config.LinkColumn("doi"),
            "id": st.column_config.LinkColumn("id")
        },
        hide_index=True,
        )
    selected_cluster = df_selected['cluster'].iloc[0]
    st.write(selected_cluster)
except:
    df_selected_centroid = centroids[
        (centroids["x"] == selected_x_value)
        & (centroids["y"] == selected_y_value)
    ]
    selected_cluster = df_selected_centroid['cluster'].iloc[0]
    
    



#st.dataframe(df_selected)
#selected_cluster = df_selected['cluster'].iloc[0]
df_selected_centroid = centroids[
    (centroids['cluster'] == selected_cluster)
]
st.write(f"selected cluster: {selected_cluster}")
st.dataframe(df_selected_centroid[['concepts','keywords','x','y']])


def get_country_cluster_sort(dc:pd.DataFrame, cl:int):
    """
    restricts the dataframe dc to cluster value cl
    and returns the results grouped by id, ror sorted
    by the some of probablity descending
    """
    dg = dc[dc['paper_cluster'] == cl].copy()
   # print(cl)
    dv = dg.groupby(['country_code'])['paper_cluster_score'].sum().to_frame()
    dv.sort_values('paper_cluster_score', ascending=False, inplace=True)
    return dv, centroids[centroids.cluster == cl]['keywords'].iloc[0]


def get_affils_cluster_sort(dc:pd.DataFrame, cl:int):
    """
    restricts the dataframe dc to cluster value cl
    and returns the results grouped by id, ror sorted
    by the some of probablity descending
    """
    dg = dc[dc['paper_cluster'] == cl].copy()
    print(cl)
    dv = dg.groupby(['id','display_name','country_code',
                     'type'])['paper_cluster_score'].sum().to_frame()
    dv.sort_values('paper_cluster_score', ascending=False, inplace=True)
    dv.reset_index(inplace=True)
    kw = centroids[centroids.cluster == cl]['keywords'].iloc[0]
    return dv, kw


def get_author_cluster_sort(dc:pd.DataFrame, cl:int):
    """
    restricts the dataframe dc to cluster value cl
    and returns the results grouped by id, ror sorted
    by the some of probablity descending
    """
    dg = dc[dc['paper_cluster'] == cl].copy()
   # print(cl)
    dv = dg.groupby(['paper_author_id','paper_author_display_name',
                    'display_name',
                     'country_code'])['paper_cluster_score'].sum().to_frame()
    dv.sort_values('paper_cluster_score', ascending=False, inplace=True)
    dv.reset_index(inplace=True)
    return dv, centroids[centroids.cluster == cl]['keywords'].iloc[0]



tab1, tab2, tab3 = st.tabs(["Countries", "Affiliations", "Authors"])

dvauthor, kwwuathor = get_author_cluster_sort(dftriple, selected_cluster)
#st.dataframe(dvauthor)


dvaffils, kwwaffils = get_affils_cluster_sort(dftriple, selected_cluster)
        
dc, kw = get_country_cluster_sort(dftriple, selected_cluster)

with tab1:
    st.dataframe(dc)
with tab2:
    st.markdown("highlight and click a value in the **id** column to be given more information")
    st.data_editor(
        dvaffils,
        column_config={
            "id": st.column_config.LinkColumn("id"),
        },
        hide_index=True,
    )
   # st.dataframe(dvaffils)
with tab3:
    st.write("highlight and click a value in the **paper_author_id** to be given more information")
    st.data_editor(
        dvauthor,
        column_config={
            "paper_author_id": st.column_config.LinkColumn("paper_author_id")
        },
        hide_index=True,
    )
    #st.dataframe(dvautho