import streamlit as st

# Sidebar for navigation
st.sidebar.markdown("## Navigation")
st.sidebar.button("Home")
st.sidebar.button("Analytics")
st.sidebar.button("Settings")

# Larger sidebar for chat history
with st.sidebar:
    st.markdown("## Chat History")
    for i in range(10):
        st.markdown(f"**Task {i+1}**: Some example task details go here.")

# Header
st.markdown(
    """
    <style>
        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 10px 0;
            border-bottom: 1px solid #e6e6e6;
        }
        .header .title {
            font-size: 24px;
            font-weight: bold;
        }
        .header .toggle {
            margin: 0 20px;
        }
        .header .profile {
            display: flex;
            align-items: center;
        }
        .header .profile img {
            border-radius: 50%;
            width: 40px;
            height: 40px;
        }
    </style>
    <div class="header">
        <div class="title">Charter</div>
        <div class="toggle">
            <label class="switch">
                <input type="checkbox">
                <span class="slider round"></span>
            </label>
        </div>
        <div class="profile">
            <img src="https://via.placeholder.com/40" alt="User Profile">
        </div>
    </div>
    """, unsafe_allow_html=True
)

# Main content area for chatbot interface
st.markdown("### Real Estate software provider survey analysis")
st.markdown("7 hours ago")
st.markdown("Creating a simple backend API for managing user data. The API should allow clients to perform basic CRUD operations (Create, Read, Update, Delete) on user records stored in memory.")

# Placeholder for chatbot and other content
st.text_input("I noticed an interesting correlation between brand awareness and willingness to pay. Would you like me to show you?")

# Placeholder for chart
st.bar_chart(data={
    'Version 1': [10, 20, 30, 40],
    'Version 2': [20, 30, 40, 50],
    'Version 3': [30, 40, 50, 60],
    'Version 4': [40, 50, 60, 70],
    'Version 5': [50, 60, 70, 80]
})

# CSS for custom styles
st.markdown(
    """
    <style>
        .sidebar .sidebar-content {
            padding-top: 20px;
        }
        .css-1d391kg {
            padding-top: 20px;
        }
    </style>
    """, unsafe_allow_html=True
)

# Run the Streamlit app
if __name__ == "__main__":
    st.run()
