import os
from flask import Flask, request, jsonify, render_template, redirect, url_for
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd

app = Flask(__name__)

# Google Sheets API setup
credentials_file = "credentials/named-totality-434615-h9-6f17d7a5f085.json"
sheet_name = "WLF_Alumni_Database"
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials = Credentials.from_service_account_file(credentials_file, scopes=scope)
client = gspread.authorize(credentials)
spreadsheet_id = "1HWo5mEVtSiMbIgnwt6_fHLmB_tA_JRgWgmtHCx76WP8"
sheet = client.open_by_key(spreadsheet_id).sheet1

# Function to fetch data from Google Sheets
def fetch_data():
    data = sheet.get_all_records()
    return pd.DataFrame(data)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Regardless of the entered credentials, redirect to the dashboard
        return redirect(url_for('dashboard'))  # Redirect to the dashboard page

    # Render the login form if the method is GET
    return render_template('login.html')

@app.route('/data', methods=['POST'])
def receive_data():
    jsinputdata = request.json
    mentor_domain = jsinputdata.get("Domain", "")  
    mentor_company = jsinputdata.get("Company", "")
    mentor_degree = jsinputdata.get("Degree", "")
    mentor_experience = jsinputdata.get("Experience", "")

    print(f"Received: {mentor_domain}, {mentor_company}, {mentor_degree}, {mentor_experience}")

    df = fetch_data()
    
    filtered_data = df[
        (df["Domain of Expertise"] == mentor_domain if mentor_domain else True) &
        (df["Current_Occupation Organization"] == mentor_company if mentor_company else True) &
        (df["Stream"] == mentor_degree if mentor_degree else True) &
        (df["Level of Expertise"] == mentor_experience if mentor_experience else True)
    ]
    
    if not filtered_data.empty:
        result = filtered_data[[ 
            "First Name", "Last Name", "Stream", "Phone No", "Mail ID", 
            "LinkedIn Profile", "Current_Occupation Role", 
            "Current_Occupation Organization", "Domain of Expertise", 
            "Level of Expertise"
        ]].to_dict(orient='records')
        return jsonify(result)

    return jsonify({"message": "No matching records found."}), 404

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        return redirect(url_for('dashboard'))  # Redirect to dashboard route
    return render_template('register.html')

@app.route('/mentorships', methods=['GET', 'POST'])
def mentorships():
    if request.method == 'POST':
        # Get form data from POST request
        degree = request.form.get('degree')
        domain = request.form.get('domain')
        company = request.form.get('company')
        experience = request.form.get('experience')

        # Fetch alumni data from Google Sheets
        df = fetch_data()

        # Filter data based on the provided criteria
        filtered_data = df[
            (df["Domain of Expertise"] == domain if domain else True) &
            (df["Current_Occupation Organization"] == company if company else True) &
            (df["Stream"] == degree if degree else True) &
            (df["Level of Expertise"] == experience if experience else True)
        ]
        
        # Convert filtered data to a list of dictionaries
        if not filtered_data.empty:
            alumni = filtered_data[[
                "First Name", "Last Name", "Stream", "Phone No", "Mail ID",
                "LinkedIn Profile", "Current_Occupation Role",
                "Current_Occupation Organization", "Domain of Expertise", 
                "Level of Expertise"
            ]].to_dict(orient='records')
        else:
            alumni = []

        # Return the rendered template with the filtered alumni data
        return render_template('mentorships.html', alumni=alumni)

    # Handle GET request (initial page load)
    return render_template('mentorships.html', alumni=[])

@app.route('/internships')
def internships():
    return render_template('internships.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/qa_board')
def qa_board():
    return render_template('qa_board.html')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)  # Run Flask in debug mode
