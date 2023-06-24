import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
import seaborn as sns
from PIL import Image
import plotly.express as px


def corr(df):
   corr = df.corr(method='spearman')
   return sns.heatmap(corr, annot=True)


def bat_first_win_pct(df):
    bat_count = 0
    bat_team = []
    bowl_count = 0
    bowl_team = []
    for i, j in enumerate(df['Margin']):
        if type(j) in (list, tuple, dict, str):
            if 'runs' in j:
                bat_count += 1
                bat_team.append(df['Winner'][i])
            elif 'wickets' in j:
                bowl_count += 1
                bowl_team.append((df['Winner'][i]))
        else:
            pass
    total_count = bat_count + bowl_count
    bat_pct = (bat_count / total_count) * 100
    bat_pct = round(bat_pct, 2)
    bat_pct = str(bat_pct) + '%'
    bowl_pct = (bowl_count / total_count) * 100
    bowl_pct = round(bowl_pct, 2)
    bowl_pct = str(bowl_pct) + '%'

    return bat_team, bowl_team, bowl_pct, bat_pct


def top_teams_on_chasing_defending(bat_team, bowl_team):
    temp1 = bat_team
    temp2 = bowl_team
    temp1 = list(set(temp1))
    temp2 = list(set(temp2))
    top5_def = []
    team1 = []
    team2 = []
    top5_chs = []
    for t in temp1:
        c = bat_team.count(t)
        if c > 1:
            team1.append(t)
            top5_def.append(c)
    for t in temp2:
        c = bowl_team.count(t)
        if c > 1:
            team2.append(t)
            top5_chs.append(c)
    return top5_def, top5_chs, team1, team2


def batting_stats(attr):
    if attr != 'SR':
        overall_data = batting_summary.groupby(['Country', 'Batter'], as_index=False).agg({attr: 'sum'})
        sorted_data = overall_data.sort_values(by=attr, ascending=False)
        top_10_bat_data = sorted_data[:10]
    elif attr == 'SR':
        overall_data = batting_summary.groupby(['Country', 'Batter'], as_index=False).agg(
            {attr: 'mean', 'Balls': 'sum'})
        filtered_data = overall_data[overall_data['Balls'] > 20]
        sorted_data = filtered_data.sort_values(by=attr, ascending=False)
        top_10_bat_data = sorted_data[:10]

    return top_10_bat_data


def bowling_stats(attr):
    if attr != 'ECON' and attr != 'WD':
        overall_data = bowling_summary.groupby(['Country', 'Bowler'], as_index=False).agg({attr: 'sum'})
        sorted_data = overall_data.sort_values(by=attr, ascending=False)
        top_10_bowl_data = sorted_data[:10]
    elif attr == 'WD':
        overall_data = bowling_summary.groupby(['Country', 'Bowler'], as_index=False).agg({attr: 'sum', 'NB': 'sum'})
        sorted_data = overall_data.sort_values(by=attr, ascending=False)
        top_10_bowl_data = sorted_data[:10]
    elif attr == 'ECON':
        overall_data = bowling_summary.groupby(['Country', 'Bowler'], as_index=False).agg({attr: 'mean', 'Overs': sum})
        filtered_data = overall_data[overall_data['Overs'] > 15]
        sorted_data = filtered_data.sort_values(by=attr, ascending=True)
        top_10_bowl_data = sorted_data[:10]
    return top_10_bowl_data


def Batter_Perf(option):
    df = batting_summary[batting_summary['Batter'] == option]
    return df


def Bowler_Perf(option1):
    df = bowling_summary[bowling_summary['Bowler'] == option1]
    return df


# importing data through scrapped data which was transformed into dataframe and then exported to csv
batting_summary = pd.read_csv('batting_summary_T20worldcup2022.csv')
bowling_summary = pd.read_csv('bowling_summary_T20worldcup2022.csv')
match_summary = pd.read_csv('T20_worldcup_2022_match_summary.csv')

# list of abandoned and no result matches
abandoned_matches = match_summary[match_summary['Winner'] == 'abandoned']
no_result_matches = match_summary[match_summary['Winner'] == 'no result']

# replacing empty columns with Nan values
match_summary['Margin'] = match_summary.Margin.replace('', 'NaN')

# dropping unnamed column from
batting_summary = batting_summary.drop("Unnamed: 0", axis=1)
bowling_summary = bowling_summary.drop("Unnamed: 0", axis=1)

# Converting Minutes and SR into integer and float respectively
batting_summary['Minutes'] = batting_summary['Minutes'].str.replace('-', '1')
batting_summary['SR'] = batting_summary['SR'].str.replace('-', '0')

batting_summary['Minutes'] = batting_summary['Minutes'].astype(int)
batting_summary['SR'] = batting_summary['SR'].astype(float)

#numeric data frame
corr_df_bat = batting_summary.select_dtypes(include=np.number)


bat_team, bowl_team, bowl_pct, bat_pct = bat_first_win_pct(match_summary)
top_def, top_chs, team1, team2 = top_teams_on_chasing_defending(bat_team, bowl_team)

# Impact player
Impact_Player = batting_summary.groupby(['Batter'], as_index=False) \
    .agg({'Runs': 'sum', 'Balls': 'sum', 'Minutes': 'sum', 'SR': 'mean'})

filtered_values = np.where((Impact_Player['SR'] >= 180) & (Impact_Player['Balls'] > 80))
filtered_df = Impact_Player.loc[filtered_values]

# Attributes for spider plot
r = list(filtered_df.values[0])[1:]
theta = list(filtered_df.columns)[1:]

# Introduction to streamlit website
st.set_page_config(layout="wide")

col1_0, col1, col1_1 = st.columns([3.3, 8, 2])

with col1:
    st.title("Analysis on T20 World cup 2022")

with col1_1:
    st.write('Streamlit web app by [Affan](https://www.linkedin.com/in/affankm/)')

# Description for the website

col2_0, col2 = st.columns([10, .1])

with col2_0:
    st.text('')
    st.write("""The T20 World Cup is one of the most highly-anticipated events in the world of cricket. 
    Taking place every two years, the tournament brings together the best teams from around the globe to compete 
    for the title of world champion. The 2022 edition of the tournament is the eighth edition, and which was played in 
    Australia. With teams from all over the world preparing to compete, the tournament promises to be one of the 
    most exciting and competitive yet. In this analysis we will analyze overal T20 world cup 2022 and also  we will
    take a closer look at the teams, players and their performance.
    """)

# Embedding the data which we collected by scraping
col3_0, col3, col3_1 = st.columns((10, .1, .1))
with col3_0:
    st.markdown("")
    expander = st.expander('''You can click here to see the raw data of overall T20 WorldCup Match Summary 
    here:point_right:''')
    with expander:
        st.dataframe(data=match_summary.reset_index(drop=True))
    expander1 = st.expander('You can click here to see the raw data of batting_summary here:point_right:')
    with expander1:
        st.dataframe(data=batting_summary.reset_index(drop=True))
    expander2 = st.expander('You can click here to see the raw data of bowling_summary here:point_right:')
    with expander2:
        st.dataframe(data=bowling_summary.reset_index(drop=True))
st.text('')

# Overall summary of the T20 Worldcup

col4_0, col4 = st.columns([10, .1])

with col4_0:
    st.text('')
    st.subheader("Overall summary of this worldcup")

col5_0, col5, col5_1 = st.columns([10, 10, 20])

with col5_0:
    st.text('')
    st.write('Tournament Start Date')
    st.write('Host')
    st.write('Number of Teams Participated')
    st.write('Total Number of Matches Played')
    st.write('Winning Percentage While Batting First')
    st.write('Number of Matches Abandoned')
    st.write('Number of Matches With No Result')
    st.write('Finals Match Date')
    st.write('Winner')

with col5:
    st.text("")
    st.write(match_summary['Match Date'][0])
    st.write('Australia')
    st.write(str(len(set(match_summary['Team 1']))))
    st.write(str(len(match_summary)))
    st.write(bat_pct)
    st.write(str(len(abandoned_matches)))
    st.write(str(len(no_result_matches)))
    st.write(match_summary['Match Date'][len(match_summary['Match Date']) - 1])
    st.write(match_summary['Winner'][len(match_summary['Winner']) - 1])

with col5_1:
    image = Image.open('download.jpeg')
    new_image = image.resize((600, 400))
    st.image(new_image)

col6_0, col6_1, col6_2, col6_3 = st.columns([7, .1, 7, .1])

with col6_0:
    st.text("")
    st.subheader("Top Five Teams Winning games by Defending Target")
    st.write(px.bar(x=team1, y=top_def, width=600, height=400))
    st.text("")
    st.write("""By seeing above chart we can clearly say that India and New Zealand has enjoyed batting first 
    and winning three matches equally """)

with col6_2:
    st.text("")
    st.subheader("Top Five Teams Winning games by Chasing Target")
    st.write(px.bar(x=team2, y=top_chs, width=600, height=400))
    st.text("")
    st.write("""By seeing above chart we can clearly say that England has enjoyed batting second 
        and winning four matches """)

col7_0, col7 = st.columns([10, .1])

with col7_0:
    st.text("")
    st.subheader('Relationship between attributes in batting summary')

col8_0, col8, col8_1 = st.columns([10, .1, 10])

with col8_0:
    st.text("")
    fig = plt.figure(figsize=(8, 4))
    corr = corr(corr_df_bat)
    st.pyplot(fig)

with col8_1:
    st.text("")
    st.text("")
    st.text("")
    st.text("")
    st.write("""The relationship between attributes of batting_summary is done by using spearman method of
                 correlation. If the values are in positive then the correlation is positive otherwise if the 
                 values are in negative then the correlation is negative. For strong correlation we will set threshold 
                 as 0.5
                 """)
    st.text("")
    st.write("""We can observe from the chart that all the values regarding batting_position attribute are 
                 negative.Hence if the batting order increase the other attributes are going down. But except the 
                 position attribute each and every other attribute is in positive correlation.""")

col9_0, col9 = st.columns([10, .1])

with col9_0:
    st.text("")
    st.subheader('Relationship between attributes in bowling summary')

col10_0, col10, col10_1 = st.columns([10, .1, 10])

with col10_0:
    st.text("")
    fig1, ax = plt.subplots()
    #sns.heatmap(bowling_summary.corr(method='spearman'), annot=True, ax=ax)
    #st.write(fig1)

with col10_1:
    st.text("")
    st.text("")
    st.text("")
    st.text("")
    st.write("""The relationship between attributes of bowling_summary is done by using spearman method of
                 correlation. If the values are in positive then the correlation is positive otherwise if the 
                 values are in negative then the correlation is negative. For strong correlation we will set threshold 
                 as 0.5""")
    st.text("")
    st.write(""" 
                Negative relation between attributes:

                 1) As Economy increases then number of 0s and Wickets decreases
                 """)
    st.text("")
    st.write(""" 
                Positive relation between attributes:

                 1) As Economy increases then number of 4s and 6s increases
                 2) Runs given by bowler increases then number of 4s and 6s increases
                 3) AS number of overs increases then Wickets, 0s, Runs increases""")

col11_0, col11 = st.columns([5, 7])

with col11_0:
    st.text("")
    st.subheader("Impact Player of the Tournament")
    name = list(filtered_df['Batter'])[0]
    runs = list(filtered_df['Runs'])[0]
    balls = list(filtered_df['Balls'])[0]
    Min = list(filtered_df['Minutes'])[0]
    SR = list(filtered_df['SR'])[0]

    st.text("")
    st.write('Name : ', name)
    st.text("")
    st.write('Runs : ', str(runs))
    st.text("")
    st.write('Balls : ', str(balls))
    st.text("")
    st.write('Minutes : ', str(Min))
    st.text("")
    st.write('Strike Rate : ', str(SR)[:5])

with col11:
    st.text("")
    fig = px.line_polar(r=r, theta=theta)
    fig.update_traces(fill='toself')
    st.write(fig)

col12_0, col12 = st.columns([10, .1])

with col12_0:
    st.subheader("Batting Stats")

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["Most Runs ", "Most 4s", "Most 6s", "Best Strike Rate", "Most Balls Faced"
                                                 , "Number of Minutes Stayed on Crease"])

with tab1:
    data = batting_stats('Runs')
    st.table(data)
with tab2:
    data = batting_stats('4s')
    st.table(data)
with tab3:
    data = batting_stats('6s')
    st.table(data)
with tab4:
    data = batting_stats('SR')
    st.table(data)
with tab5:
    data = batting_stats('Balls')
    st.table(data)
with tab6:
    data = batting_stats('Minutes')
    st.table(data)

# Bowling Stats
col13_0, col13 = st.columns([10, .1])

with col13_0:
    st.subheader("Bowling Stats")

tab7, tab8, tab9, tab10, tab11, tab12, tab13, tab14 = st.tabs(["Most Wickets ", "Most 4s Given", "Most 6s Given",
                                                               "Best Economy", "Most Dot Balls", "Most Maidens",
                                                               "Runs Leaked", "Extras"])

with tab7:
    data = bowling_stats('Wickets')
    st.table(data)
with tab8:
    data = bowling_stats('4s')
    st.table(data)
with tab9:
    data = bowling_stats('6s')
    st.table(data)
with tab10:
    data = bowling_stats('ECON')
    st.table(data)
with tab11:
    data = bowling_stats('0s')
    st.table(data)
with tab12:
    data = bowling_stats('Maidens')
    st.table(data)
with tab13:
    data = bowling_stats('Runs')
    st.table(data)
with tab14:
    data = bowling_stats('WD')
    st.table(data)

col14_0, col14 = st.columns([10, .1])

with col14_0:
    st.text("")
    st.subheader("Individual Performance of batter")

batters = list(set(batting_summary['Batter']))
batters.insert(0, '')  # for writing option in select boc
option = st.selectbox("Pick on of the Batter to see their Individual Perfomance", batters)

col15_0, col15 = st.columns([10, .1])

with col15_0:
    st.text("")
    st.write('Perfomance of ', option, 'in this tournament is ')

col16_0, col16, col16_1 = st.columns([11, .1, 14])

with col16_0:
    st.text("")
    batter_metric = Batter_Perf(option)
    st.table(batter_metric)

with col16_1:
    st.text("")
    Innings = list(range(1, len(batter_metric) + 1))
    runs = list(batter_metric['Runs'])
    SR = list(batter_metric['SR'])

    chart_df = pd.DataFrame(
        {'innings': Innings, 'runs': runs, 'strike_rate': SR, 'Balls': list(batter_metric['Balls'])})
    fig = px.line(chart_df, x='innings', y='runs', title='Runs vs SR vs Balls', animation_group='runs')
    fig.add_scatter(x=chart_df['innings'], y=chart_df['strike_rate'], mode='lines', name='Strike Rate')
    fig.add_scatter(x=chart_df['innings'], y=chart_df['Balls'], mode='lines', name='Balls')
    st.write(fig)

# Individual perfomance of bowler

col17_0, col17 = st.columns([10, .1])

with col17_0:
    st.text("")
    st.subheader("Individual Performance of bowler")

bowlers = list(set(bowling_summary['Bowler']))
bowlers.insert(0, '')  # for writing option in select boc
option1 = st.selectbox("Pick on of the Bowler to see their Individual Perfomance", bowlers)

col18_0, col18 = st.columns([10, .1])

if option1 != None:
    with col18_0:
      st.text("")
      st.write('Perfomance of ', option1, 'in this tournament is ')

    col19_0, col19, col19_1 = st.columns([11, .1, 14])

    with col19_0:
       st.text("")
       bowler_metric = Bowler_Perf(option1)
       st.table(bowler_metric)

    with col19_1:
       st.text("")
       Innings = list(range(1, len(bowler_metric) + 1))
       Wickets = list(bowler_metric['Wickets'])
       ECON = list(bowler_metric['ECON'])

       chart_df1 = pd.DataFrame(
        {'innings': Innings, 'Wickets': Wickets, 'ECON': ECON, 'Runs': list(bowler_metric['Runs'])})
       fig = px.line(chart_df1, x='innings', y='Wickets', title='Wickets vs ECON vs Runs', animation_group='Wickets')
       fig.add_scatter(x=chart_df1['innings'], y=chart_df1['ECON'], mode='lines', name='Economy')
       fig.add_scatter(x=chart_df1['innings'], y=chart_df1['Runs'], mode='lines', name='Runs')
       st.write(fig)
