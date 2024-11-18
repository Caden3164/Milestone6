import os
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from openai import OpenAI

# Set Streamlit page config to wide layout
st.set_page_config(layout="wide")

# Initialize the OpenAI client using the API key from the environment variable
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

# Custom CSS for styling
st.markdown(
    """
    <style>
    /* Sidebar Styling */
    section[data-testid="stSidebar"] .css-1aumxhk {
        font-size: 24px !important;
    }
    section[data-testid="stSidebar"] h1 {
        font-size: 26px !important;
        color: #4CAF50;
    }
    section[data-testid="stSidebar"] .stRadio > label {
        font-size: 24px !important;
        color: #333;
    }
    section[data-testid="stSidebar"] .stRadio > div > label > div {
        font-size: 20px !important;
        color: #333;
    }

    /* Main Content Styling */
    .main .block-container {
        max-width: 90%;
        padding-top: 2rem;
    }

    /* Header Styling */
    h1.title {
        font-size: 36px;
        color: #4CAF50;
        text-align: center;
    }
    h2.header {
        font-size: 28px;
        color: #333;
    }

    /* Change the background color of the app */
    .main {
        background-color: #e6f7ff; /* Light blue color */
    }

    /* Optional: Change the sidebar background color */
    section[data-testid="stSidebar"] {
        background-color: #d9f2f8; /* Slightly different light blue */
    }
    </style>
    """,
    unsafe_allow_html=True
)


# Define the get_completion function
def get_completion(prompt, model="gpt-3.5-turbo"):
    completion = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are an environmental specialist. Provide concise, personalized water-saving advice based on the user's input and data."},
            {"role": "user", "content": prompt},
        ]
    )
    return completion.choices[0].message.content

# Function to analyze faucet data and generate summary/graph
# Function to analyze faucet data and generate summary/graph
def analyze_faucet_data(file_path=r"C:\Users\caden\Desktop\118i_Project\faucet_usage_data.csv"):
    try:
        # Load and process data
        df = pd.read_csv(file_path)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['hour'] = df['timestamp'].dt.hour

        # Aggregate data
        total_usage = df.groupby("faucet_id")["usage_liters"].sum()
        hourly_usage = df.groupby("hour")["usage_liters"].sum()

        # Convert 24-hour clock to 12-hour clock with AM/PM
        hourly_usage.index = hourly_usage.index.map(
            lambda x: f"{x % 12 or 12} {'AM' if x < 12 else 'PM'}"
        )

        # Peak usage hour
        peak_usage_hour = hourly_usage.idxmax()

        # Pie chart for total water usage by faucet
        st.subheader("Total Water Usage by Faucet")
        fig_pie, ax_pie = plt.subplots(figsize=(5, 5))
        ax_pie.pie(
            total_usage,
            labels=total_usage.index,
            autopct='%1.1f%%',
            startangle=90,
            textprops={'fontsize': 10}
        )
        ax_pie.set_title("Water Usage by Faucet", fontsize=14)
        ax_pie.axis('equal')  # Equal aspect ratio ensures the pie chart is circular
        st.pyplot(fig_pie)

        # Add a summary text
        most_used_faucet = total_usage.idxmax()
        st.markdown(
            f"""
            - **Most Frequently Used Faucet**: {most_used_faucet}
            - **Peak Water Usage Hour**: {peak_usage_hour}
            """
        )

        # Line chart for hourly water usage trend
        st.subheader("Hourly Water Usage Trend")
        fig_line, ax_line = plt.subplots(figsize=(8, 5))
        hourly_usage.plot(kind="line", ax=ax_line, marker='o', color='blue', linewidth=2)

        # Customize the axes for readability
        ax_line.set_title("Hourly Water Usage Trend", fontsize=14)
        ax_line.set_xlabel("Time of Day (12-hour clock)", fontsize=12)
        ax_line.set_ylabel("Water Usage (liters)", fontsize=12)
        ax_line.grid(axis='y', linestyle='--', alpha=0.7)

        # Adjust the Y-axis scale to make it readable
        y_max = hourly_usage.max()
        ax_line.set_ylim(0, y_max * 1.2)  # Add a 20% margin above the highest value
        st.pyplot(fig_line)

        # Dynamically generate advice using the OpenAI API
        peak_hour = hourly_usage.idxmax()  # Identify the peak usage hour
        total_usage_liters = total_usage.sum()  # Calculate total water usage
        peak_usage = hourly_usage.max()  # Peak water usage in liters

        # Create a prompt for the API
        prompt = f"""
        Based on the user's water usage data:
        - The total water usage is {total_usage_liters:.2f} liters.
        - The peak water usage hour is {peak_hour} with {peak_usage:.2f} liters used.

        Provide personalized advice to help the user reduce water usage during peak hours and suggest habits to save water. Remember that the user may not be experienced in technical terminology, so provide very general advice that the average person can understand.
        """

        # Call the OpenAI API for advice
        advice = get_completion(prompt)

        # Display the dynamically generated advice
        st.markdown("### AI-Generated Water-Saving Advice")
        st.write(advice)

        st.markdown(
            "The graph above shows the total water usage by hour. Pay attention to the peak usage times and adjust your water habits accordingly to save water."
        )

    except Exception as e:
        st.error(f"An error occurred: {e}")

    except FileNotFoundError:
        st.error("File not found. Please ensure the file exists and try again.")



# Residential questionnaire
def residential_questionnaire():
    st.subheader("Residential Water Usage Questionnaire")
    household_size = st.selectbox("Household size:", ["1", "2", "3", "4", "5+"])
    activities = st.selectbox("Water-intensive activities frequency:", ["Daily", "Several times a week", "Weekly", "Rarely"])
    practices = st.multiselect("Water-saving practices:", ["Low-flow showerheads", "Faucet aerators", "Reusing water", "Reducing shower time", "None"])
    motivation = st.selectbox("Primary motivation for saving water:", ["Environmental concern", "Reducing bills", "Water scarcity", "Other"])

    # Generate a prompt with motivations explicitly included
    prompt = f"""
    User Details:
    - Household Size: {household_size}
    - Water-Intensive Activities: {activities}
    - Water-Saving Practices: {', '.join(practices)}
    - Motivation: {motivation}
    
    Provide concise, actionable advice tailored to their motivation and water usage. After providing advice, also provide some simple statistics to support how much water or money that making these changes could save the user. Remember that the user might not be technical or intelligent, so keep it clear and simple. Include the statistics together with the water saving advice instead of in its own section. concisely elaborate on the statistics to explain to the user what the statistics mean, because the everyday user might not understand gallons or litres.
    """
    if st.button("Get Advice"):
        advice = get_completion(prompt)
        st.success("Personalized Advice:")
        st.write(advice)

# Farmer's water usage questionnaire
def farmers_questionnaire():
    st.subheader("Efficient Water Use on Your Farm")
    crop_type = st.selectbox("Type of crop:", ["Wheat", "Corn", "Rice", "Soybeans", "Other"])
    irrigation_method = st.selectbox("Irrigation method:", ["Drip", "Sprinkler", "Flood", "Furrow", "Other"])
    soil_type = st.selectbox("Soil type:", ["Clay", "Sandy", "Loamy", "Silty", "Peaty", "Other"])
    avg_rainfall = 14.02  # Example value for San Jose, CA
    st.write(f"Using a preset average annual rainfall value: {avg_rainfall} inches.")


    prompt = f"""
    The farmer has provided the following details:
    - Crop Type: {crop_type}
    - Irrigation Method: {irrigation_method}
    - Soil Type: {soil_type}
    - Average Annual Rainfall: {avg_rainfall} inches
    
    Provide advice on optimal water usage and irrigation practices considering the type of crop, irrigation method, soil type, and rainfall.
    """
    if st.button("Get Water Usage Advice for Farming"):
        advice = get_completion(prompt)
        st.success("Personalized Water-Saving Advice for Farmers")
        st.write(advice)

# Water usage calculator
def water_usage_calculator():
    st.subheader("Water Usage Calculator")
    shower_time = st.number_input("How many minutes do you shower daily?", min_value=0)
    dishwashing_loads = st.number_input("How many loads of dishes do you wash per week?", min_value=0)
    laundry_loads = st.number_input("How many loads do you do laundry per week?", min_value=0)
    watering_time = st.number_input("How many minutes do you water the garden daily?", min_value=0)

    shower_usage_per_minute = 2.1  # gallons
    dishwashing_usage_per_load = 6   # gallons
    laundry_usage_per_load = 15      # gallons
    watering_usage_per_minute = 3     # gallons

    daily_usage = (
        shower_time * shower_usage_per_minute +
        (dishwashing_loads * dishwashing_usage_per_load / 7) +
        (laundry_loads * laundry_usage_per_load / 7) +
        (watering_time * watering_usage_per_minute)
    )
    monthly_usage = daily_usage * 30  # Approximate monthly usage

    st.write(f"**Daily Water Usage:** {daily_usage:.2f} gallons")
    st.write(f"**Monthly Water Usage:** {monthly_usage:.2f} gallons")

# Main app with improved session state handling
def main():
    st.markdown("<h1 class='title'>Water Usage Application</h1>", unsafe_allow_html=True)

    # Initialize session state for navigation
    if "page" not in st.session_state:
        st.session_state.page = "Home"

    # Sidebar navigation
    st.sidebar.title("Navigation")
    nav_options = ["Home", "Residential Advice", "Analyze Faucet Data", "Farmer's Water Usage", "Water Usage Calculator"]
    selected_page = st.sidebar.radio("Choose a section", nav_options, index=nav_options.index(st.session_state.page))

    # Set session state based on sidebar selection
    if selected_page != st.session_state.page:
        st.session_state.page = selected_page

    # Home page functionality
    if st.session_state.page == "Home":
        st.markdown("### Welcome to the Water Usage Application!")
        st.markdown(
            "This app is designed to help you manage and conserve water effectively, "
            
        )
        user_type = st.radio(
            "Please select your role:",
            ["Everyday Water User", "Agricultural Producer"]
        )
        if st.button("Submit"):
            if user_type == "Everyday Water User":
                st.session_state.page = "Residential Advice"
            elif user_type == "Agricultural Producer":
                st.session_state.page = "Farmer's Water Usage"

    # Residential section
    elif st.session_state.page == "Residential Advice":
        st.button("Back to Home", on_click=lambda: setattr(st.session_state, "page", "Home"))
        residential_questionnaire()

    # Faucet data analytics section
    elif st.session_state.page == "Analyze Faucet Data":
        st.button("Back to Home", on_click=lambda: setattr(st.session_state, "page", "Home"))
        analyze_faucet_data()

    # Farmer's section
    elif st.session_state.page == "Farmer's Water Usage":
        st.button("Back to Home", on_click=lambda: setattr(st.session_state, "page", "Home"))
        farmers_questionnaire()

    # Water usage calculator section
    elif st.session_state.page == "Water Usage Calculator":
        st.button("Back to Home", on_click=lambda: setattr(st.session_state, "page", "Home"))
        water_usage_calculator()


if __name__ == "__main__":
    main()

