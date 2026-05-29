import warnings
warnings.filterwarnings('ignore')

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

import mysql.connector
import sqlite3
from sqlalchemy import create_engine

engine = create_engine (
    "mysql+pymysql://root:12345@localhost/traffic_db"
)
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="12345",
    database="traffic_db"
)

print("Connected Successfully")

st.title("🚗 Traffic Crash Analytics & Safety Intelligence Platform")

# Radio navigation menu
menu = st.radio(
    "Navigation Menu",
    ["🏠 Home", "🔎 Queries",]
)

# ---------------- HOME ----------------
if menu == "🏠 Home":
    st.header("Welcome to Crash Analytics Platform 🚗")

    st.write("""
    This platform helps analyze traffic crash data to understand:
    - Crash patterns 🚨
    - Common causes ⚠️
    - Time-based trends ⏰
    - Safety insights 🛣️
    """)

# ---------------- QUERIES ----------------
elif menu == "🔎 Queries":
    st.header("Run SQL Queries on Crash Data")

# Sidebar menu
query_option = st.selectbox(
    "Choose a Query",
    [
        "1.Find the top 5 most dangerous combinations of weather and crash type based on total crashes.",
        "2.Identify the top 10 streets with the highest number of injury crashes.",
         "3.Find the percentage of crashes that resulted in injuries for each crash type.",
         "4.Determine the peak crash hour for each month.",
          "5.Find the top 5 primary causes of crashes during night time (CRASH_HOUR ≥ 18).", 
         "6.Compare average number of injuries in daylight vs darkness conditions.",
         "7.Find which traffic control device type has the highest average injuries per crash.",
          "8.Identify the top 5 locations (latitude/longitude) with the highest crash frequency.",
         "9.Find the top 5 streets with the highest injury rate, considering only streets with more than 100 crashes.", 
          "10.For each year, identify the most common crash.",
          "11.Find the day of the week with the highest average crashes per hour.",
         "12. Identify high-risk time slots.",
          "13.Find the top 3 contributing causes for each crash type.",
          "14.Calculate the year-over-year growth rate of crashes.",
          "15.Identify hotspot zones.",

    ]
)

# Query condition


if query_option == "1.Find the top 5 most dangerous combinations of weather and crash type based on total crashes.":

    query = """
    SELECT 
        WEATHER_CONDITION,
        FIRST_CRASH_TYPE,
        COUNT(*) AS TOTAL_CRASHES
    FROM crashes
    GROUP BY WEATHER_CONDITION, FIRST_CRASH_TYPE
    ORDER BY TOTAL_CRASHES DESC
    LIMIT 5;
    """

    dangerous_combinations = pd.read_sql(query, con=engine)
    st.dataframe(dangerous_combinations)
    st.subheader("Business Insight")
    st.info("""
    Adverse weather conditions significantly increase certain types of crashes. 
    Traffic authorities can use this insight to improve road safety and accident prevention strategies during risky weather periods.
    """)


elif query_option == "2.Identify the top 10 streets with the highest number of injury crashes.":

    query = """
    SELECT STREET_NAME,
           COUNT(*) AS injury_crashes
    FROM crashes
    WHERE INJURIES_TOTAL > 0
    GROUP BY STREET_NAME
    ORDER BY injury_crashes DESC
    LIMIT 10;
    """

    injuries = pd.read_sql(query, con=engine)
    st.dataframe(injuries)
    st.subheader("Business Insight")
    st.info("""
    The streets with the highest injury crashes require immediate traffic safety improvements and stricter monitoring. 
    These locations should be prioritized for better road infrastructure and accident prevention measures.
    """)


elif query_option =="3.Find the percentage of crashes that resulted in injuries for each crash type.":

    query = """
    SELECT 
        FIRST_CRASH_TYPE,
        COUNT(*) AS total_crashes,
        SUM(
            CASE
                WHEN INJURIES_TOTAL > 0 THEN 1
                ELSE 0
            END
        ) AS injury_crashes,
        ROUND(
            (
                SUM(
                    CASE
                        WHEN INJURIES_TOTAL > 0 THEN 1
                        ELSE 0
                    END
                ) * 100.0
            ) / COUNT(*),
            2
        ) AS injury_percentage

    FROM crashes

    GROUP BY FIRST_CRASH_TYPE

    ORDER BY injury_percentage DESC;
    """

    injury_percentage = pd.read_sql(query, con=engine)
    st.dataframe(injury_percentage)
    st.subheader("Business Insight")
    # Business Insight
    st.info("""
    Crash types with higher injury percentages are more dangerous and need better road safety measures, traffic control, and emergency response planning""")

elif query_option == "4.Determine the peak crash hour for each month.":

    query = """
    WITH monthly_crashes AS (
    SELECT
        MONTH(CRASH_DATE) AS CRASH_MONTH,
        CRASH_HOUR,
        COUNT(*) AS TOTAL_CRASHES
    FROM crashes
    GROUP BY MONTH(CRASH_DATE), CRASH_HOUR
),

ranked_hours AS (
    SELECT *,
           RANK() OVER (
               PARTITION BY CRASH_MONTH
               ORDER BY TOTAL_CRASHES DESC
           ) AS rnk
    FROM monthly_crashes
)

SELECT 
    CRASH_MONTH,
    CRASH_HOUR,
    TOTAL_CRASHES
FROM ranked_hours
WHERE rnk = 1
ORDER BY CRASH_MONTH;
"""

    peak_hours = pd.read_sql(query, con=engine)
    st.dataframe(peak_hours)
    st.subheader("Business Insight")
    st.info("""
    Peak crash hours vary across months, indicating changing traffic patterns and risk periods. 
    This insight can help authorities optimize traffic control and emergency response planning.
    """)

elif query_option == "5.Find the top 5 primary causes of crashes during night time (CRASH_HOUR ≥ 18).":

    query = """
    SELECT 
        PRIM_CONTRIBUTORY_CAUSE,
        COUNT(*) AS TOTAL_CRASHES
    FROM crashes
    WHERE CRASH_HOUR >= 18
    AND PRIM_CONTRIBUTORY_CAUSE IS NOT NULL
    GROUP BY PRIM_CONTRIBUTORY_CAUSE
    ORDER BY TOTAL_CRASHES DESC
    LIMIT 5;
    """

    night_causes = pd.read_sql(query, con=engine)
    st.dataframe(night_causes)
    st.subheader("Business Insight")
    st.info("""
    The major causes of night-time crashes indicate increased risks due to low visibility and unsafe driving behavior. 
    Targeted night traffic monitoring and driver awareness programs can help reduce accidents during late hours.
    """)

elif query_option=="6.Compare average number of injuries in daylight vs darkness conditions.":
    
    query=""" 
    SELECT 
    LIGHTING_CONDITION,
    ROUND(AVG(INJURIES_TOTAL), 2) AS AVG_INJURIES
    FROM crashes
    WHERE LIGHTING_CONDITION IN ('DAYLIGHT', 'DARKNESS')
    GROUP BY LIGHTING_CONDITION;
    """

    compare_average=pd.read_sql(query, con=engine)
    st.dataframe(compare_average)
    st.subheader("Business Insight")
    st.info("""
    Darkness conditions show a higher risk of severe injuries compared to daylight conditions. 
    Improved street lighting and night-time traffic enforcement can help reduce injury-related crashes.
    """)

elif query_option=="7.Find which traffic control device type has the highest average injuries per crash.":
    
    query=""" 
    SELECT 
    TRAFFIC_CONTROL_DEVICE,
    ROUND(AVG(INJURIES_TOTAL), 2) AS AVG_INJURIES
    FROM crashes
    WHERE TRAFFIC_CONTROL_DEVICE IS NOT NULL
    GROUP BY TRAFFIC_CONTROL_DEVICE
    ORDER BY AVG_INJURIES DESC
    LIMIT 5;
    """

    device_type=pd.read_sql(query, con=engine)
    st.dataframe(device_type)
    st.subheader("Business Insight")
    st.info("""
    Certain traffic control devices are associated with higher average injuries per crash, indicating potential safety or compliance issues. 
    These locations may require improved traffic management and stricter enforcement measures.
    """)

elif query_option=="8.Identify the top 5 locations (latitude/longitude) with the highest crash frequency.":

    query="""
    SELECT 
    LATITUDE,
    LONGITUDE,
    COUNT(*) AS TOTAL_CRASHES
    FROM crashes
    WHERE LATITUDE IS NOT NULL
    AND LONGITUDE IS NOT NULL
    GROUP BY LATITUDE, LONGITUDE
    ORDER BY TOTAL_CRASHES DESC
    LIMIT 5;
    """

    location_frequency=pd.read_sql(query, con=engine)
    st.dataframe(location_frequency)
    st.subheader("Business Insight")
    st.info("""
    The identified high-crash locations represent critical accident hotspots requiring immediate safety improvements. 
    Focused traffic monitoring and infrastructure upgrades at these locations can help reduce crash frequency.
    """)

elif query_option=="9.Find the top 5 streets with the highest injury rate, considering only streets with more than 100 crashes.":

    query="""
    SELECT 
    STREET_NAME,
    COUNT(*) AS TOTAL_CRASHES,
    SUM(CASE WHEN INJURIES_TOTAL > 0 THEN 1 ELSE 0 END) AS INJURY_CRASHES,
    ROUND(
        100.0 * SUM(CASE WHEN INJURIES_TOTAL > 0 THEN 1 ELSE 0 END)
        / COUNT(*),
        2
    ) AS INJURY_RATE
    FROM crashes
    WHERE STREET_NAME IS NOT NULL
    GROUP BY STREET_NAME
    HAVING COUNT(*) > 100
    ORDER BY INJURY_RATE DESC
    LIMIT 5;
    """

    street_injury=pd.read_sql(query, con=engine)
    st.dataframe(street_injury)
    st.subheader("Business Insight")
    st.info("""
    Streets with high injury rates indicate areas with severe accident impact and increased safety risks. 
    These roads should be prioritized for traffic safety measures and infrastructure improvements.
    """)


elif query_option == "10.For each year, identify the most common crash.":
    
    query = """
    WITH yearly_crashes AS (
        SELECT 
            YEAR(STR_TO_DATE(CRASH_DATE, '%%m/%%d/%%Y %%h:%%i:%%s %%p')) AS YEAR_NO,
            FIRST_CRASH_TYPE,
            COUNT(*) AS TOTAL_CRASHES
        FROM crashes
        WHERE CRASH_DATE IS NOT NULL
          AND FIRST_CRASH_TYPE IS NOT NULL
        GROUP BY 
            YEAR(STR_TO_DATE(CRASH_DATE, '%%m/%%d/%%Y %%h:%%i:%%s %%p')),
            FIRST_CRASH_TYPE
    ),

    ranked_data AS (
        SELECT 
            YEAR_NO,
            FIRST_CRASH_TYPE,
            TOTAL_CRASHES,
            RANK() OVER (
                PARTITION BY YEAR_NO
                ORDER BY TOTAL_CRASHES DESC
            ) AS RNK
        FROM yearly_crashes
    )

    SELECT 
        YEAR_NO,
        FIRST_CRASH_TYPE,
        TOTAL_CRASHES
    FROM ranked_data
    WHERE RNK = 1
    ORDER BY YEAR_NO;
    """

    try:
        each_year = pd.read_sql(query, con=engine)
        st.dataframe(each_year)
        st.subheader("Business Insight")
        st.info("""
        The most common crash types highlight recurring traffic safety challenges across different years. 
        Understanding these patterns can help authorities implement targeted accident prevention strategies.
        """)
    except Exception as e:
        st.error(f"Error: {e}")
       


elif query_option=="11.Find the day of the week with the highest average crashes per hour.":

    query="""
    SELECT 
        DAYNAME(STR_TO_DATE(CRASH_DATE, '%%m/%%d/%%Y %%h:%%i:%%s %%p')) AS DAY_NAME,
        ROUND(COUNT(*) / COUNT(DISTINCT CRASH_HOUR), 2) AS AVG_CRASHES_PER_HOUR
    FROM crashes
    WHERE CRASH_DATE IS NOT NULL
      AND CRASH_HOUR IS NOT NULL
    GROUP BY DAY_NAME
    ORDER BY AVG_CRASHES_PER_HOUR DESC
    LIMIT 1;
    """

    avg_crashes = pd.read_sql(query, con=engine)
    st.dataframe(avg_crashes)
    st.subheader("Business Insight")
    st.info("""
    Certain days experience a higher average number of crashes per hour due to increased traffic activity and congestion. 
    This insight can help optimize traffic management and road safety planning on high-risk days.
    """)


elif query_option=="12. Identify high-risk time slots.":

    query="""
      SELECT 
        CASE
            WHEN CRASH_HOUR BETWEEN 5 AND 11 THEN 'Morning'
            WHEN CRASH_HOUR BETWEEN 12 AND 16 THEN 'Afternoon'
            WHEN CRASH_HOUR BETWEEN 17 AND 20 THEN 'Evening'
            ELSE 'Night'
        END AS TIME_BUCKET,

        COUNT(*) AS INJURY_CRASHES

    FROM crashes

    WHERE INJURIES_TOTAL > 0
      AND CRASH_HOUR IS NOT NULL

    GROUP BY TIME_BUCKET

    ORDER BY INJURY_CRASHES DESC;
    """

    high_risk_slots = pd.read_sql(query, con=engine)
    st.dataframe(high_risk_slots)
    st.subheader("Business Insight")
    st.info("""
    Certain time periods experience significantly higher injury crashes due to increased traffic density and risky driving behavior. 
    This insight can help authorities strengthen traffic monitoring and safety measures during high-risk hours.
    """)

elif query_option=="13.Find the top 3 contributing causes for each crash type.":

    query="""
      WITH cause_counts AS (

        SELECT 
            FIRST_CRASH_TYPE,
            PRIM_CONTRIBUTORY_CAUSE,
            COUNT(*) AS TOTAL_CRASHES

        FROM crashes

        WHERE FIRST_CRASH_TYPE IS NOT NULL
          AND PRIM_CONTRIBUTORY_CAUSE IS NOT NULL

        GROUP BY 
            FIRST_CRASH_TYPE,
            PRIM_CONTRIBUTORY_CAUSE
    ),

    ranked_causes AS (

        SELECT *,
               ROW_NUMBER() OVER (
                   PARTITION BY FIRST_CRASH_TYPE
                   ORDER BY TOTAL_CRASHES DESC
               ) AS RN

        FROM cause_counts
    )

    SELECT 
        FIRST_CRASH_TYPE,
        PRIM_CONTRIBUTORY_CAUSE,
        TOTAL_CRASHES

    FROM ranked_causes

    WHERE RN <= 3

    ORDER BY 
        FIRST_CRASH_TYPE,
        TOTAL_CRASHES DESC;
    """

    top_causes = pd.read_sql(query, con=engine)
    st.dataframe(top_causes)
    st.subheader("Business Insight")
    st.info("""
    The leading contributing causes for each crash type highlight the major factors behind road accidents. 
    These insights can help authorities design targeted safety campaigns and preventive traffic measures.
    """)


elif query_option=="14.Calculate the year-over-year growth rate of crashes.":

    query="""
     WITH yearly_crashes AS (

        SELECT 
            YEAR(STR_TO_DATE(CRASH_DATE, '%%m/%%d/%%Y %%h:%%i:%%s %%p')) AS YEAR_NO,
            COUNT(*) AS TOTAL_CRASHES

        FROM crashes

        WHERE CRASH_DATE IS NOT NULL

        GROUP BY YEAR_NO
    ),

    yearly_growth AS (

        SELECT 
            YEAR_NO,
            TOTAL_CRASHES,

            LAG(TOTAL_CRASHES) OVER (
                ORDER BY YEAR_NO
            ) AS PREVIOUS_YEAR_CRASHES

        FROM yearly_crashes
    )

    SELECT 
        YEAR_NO,
        TOTAL_CRASHES,
        PREVIOUS_YEAR_CRASHES,

        ROUND(
            (
                (TOTAL_CRASHES - PREVIOUS_YEAR_CRASHES)
                / PREVIOUS_YEAR_CRASHES
            ) * 100,
            2
        ) AS GROWTH_RATE_PERCENT

    FROM yearly_growth

    WHERE PREVIOUS_YEAR_CRASHES IS NOT NULL

    ORDER BY YEAR_NO;
    """
        
    growth_rate = pd.read_sql(query, con=engine)
    st.dataframe(growth_rate)
    st.subheader("Business Insight")
    st.info("""
    The year-over-year crash growth rate reveals trends in road safety performance over time. 
    Increasing crash growth may indicate the need for stronger traffic management and accident prevention strategies.
    """)


elif query_option== "15.Identify hotspot zones.":

    query="""
     SELECT 
        ROUND(LATITUDE, 2) AS LAT_ZONE,
        ROUND(LONGITUDE, 2) AS LONG_ZONE,
        COUNT(*) AS TOTAL_CRASHES

    FROM crashes

    WHERE LATITUDE IS NOT NULL
      AND LONGITUDE IS NOT NULL

    GROUP BY 
        ROUND(LATITUDE, 2),
        ROUND(LONGITUDE, 2)

    ORDER BY TOTAL_CRASHES DESC

    LIMIT 10;
    """

    hotspot_zones = pd.read_sql(query, con=engine)
    st.dataframe(hotspot_zones)
    st.subheader("Business Insight")
    st.info("""
    The identified hotspot zones indicate regions with frequent crash occurrences and higher traffic risk. 
    Targeted road safety measures and better traffic management can help reduce accidents in these areas.
    """)