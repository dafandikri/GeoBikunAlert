# Import necessary modules
from flask import Flask, request, jsonify, render_template
from geopy.distance import geodesic
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import re
from apscheduler.schedulers.background import BackgroundScheduler

# Initialize Flask app
app = Flask(__name__)

# Set options to run Chrome in headless mode
options = Options()
options.add_argument("--headless")

# List to store bus locations
bus_locations = []

# Initialize scheduler
scheduler = BackgroundScheduler()

# Function to scrape website for bus locations
def scrape_website():
    # Create a new instance of the Chrome driver
    driver = webdriver.Chrome(options=options)

    # Go to the website that you want to scrape
    driver.get('https://bikun.ui.ac.id/')

    # Wait for the JavaScript to load
    driver.implicitly_wait(10)

    # Find all img tags with either of the specified src attributes
    buses = driver.find_elements(By.XPATH, '//img[@src="/static/media/new-red-bus-icon.f871610db183a6261677d9c458938611.svg" or @src="/static/media/new-blue-bus-icon.97aad2af34c681a02683f1c7afbdbb69.svg"]')

    # Clear the bus_locations list
    bus_locations.clear()

    # Extract the style attribute from each tag
    for i, bus in enumerate(buses):
        style = bus.get_attribute('style')
        match = re.search('translate3d\((.*?)px, (.*?)px', style)
        if match:
            # If a match is found, extract the value and add it to list
            x = float(match.group(1))
            y = float(match.group(2))
            
            # Adjust the x and y coordinates
            x_adjusted = x - 4
            y_adjusted = y + 62
            
            location = str(x_adjusted) + ', ' + str(y_adjusted)
            bus_locations.append({'id': i, 'coords': location})

    # Close the browser
    driver.quit()

# Call the function to scrape the website
scrape_website()

# Schedule the function to scrape the website every 10 seconds
scheduler.add_job(scrape_website, 'interval', seconds=10)

# Route to render the home page
@app.route('/')
def home():
    # Your list of pixel coordinates
    buses = bus_locations
    return render_template('index.html', buses=buses)

# Route to get bus data
@app.route('/get-bus-data')
def get_bus_data():
    return jsonify(bus_locations)

# Define the station's GPS location
station_location = (-6.361240619348628, 106.82327825578848)

# Define a proximity threshold (in meters)
proximity_threshold = 200

# Define your email settings
smtp_server = 'smtp.gmail.com'
smtp_port = 587
email_address = 'dafandikri@gmail.com'
email_password = 'rjkg nfgj deli bbrh'
to_address = 'dafandikri@gmail.com'

# List to hold buses for which notifications have been sent
notified_buses = []

# Function to clear the list of notified buses
def clear_notified_buses():
    notified_buses.clear()

# Route to save coordinates
@app.route('/save-coordinates', methods=['POST'])
def save_coordinates():
    busesLatLng = request.get_json()

    # Dictionary to hold buses that are nearing the station
    nearing_buses = {}

    # Loop through each bus
    for bus in busesLatLng:
        bus_id = bus['id']
        bus_location = bus['lat'], bus['lng']

        # Calculate the distance between the bus and the station
        distance = geodesic(station_location, tuple(bus_location)).meters

        # Check if the bus is within the proximity threshold
        if distance <= proximity_threshold:
            # The bus is nearing the station
            nearing_buses[bus_id] = bus_location
        elif bus_id in notified_buses:
            # The bus is no longer within the proximity threshold, so remove it from the notified_buses list
            notified_buses.remove(bus_id)

    # Do something with the buses that are nearing, such as sending a notification
    if nearing_buses:
        # Trigger notification for each nearing bus
        for bus_id, bus_location in nearing_buses.items():
            # Check if a notification has already been sent for this bus
            if bus_id in notified_buses:
                # Skip this bus
                continue

            print(f"Bus {bus_id} at {bus_location} is nearing the station.")
            # Trigger notification here

            # Create the email
            msg = MIMEMultipart()
            msg['From'] = email_address
            msg['To'] = to_address
            msg['Subject'] = 'Bus Nearing Station'
            body = f"Bus {bus_id} at {bus_location} is nearing the station."
            msg.attach(MIMEText(body, 'plain'))

            # Send the email
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(email_address, email_password)
            text = msg.as_string()
            server.sendmail(email_address, to_address, text)
            server.quit()

            # Add the bus ID to the list of notified buses
            notified_buses.append(bus_id)

    return jsonify({'message': 'Coordinates processed successfully'})

# Schedule the function to clear the list of notified buses every 60 seconds
scheduler.add_job(clear_notified_buses, 'interval', seconds=60)

# Function to open and close the browser
def open_and_close_browser():
    # Create a new instance of the Chrome driver with the headless option
    driver = webdriver.Chrome(options=options)

    # Open the localhost URL
    driver.get('http://localhost:5000')
    
    # Close the browser
    driver.close()

# Schedule the function to open and close the browser every 10 seconds
scheduler.add_job(open_and_close_browser, 'interval', seconds=10)

# Start the scheduler
scheduler.start()

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True, port=5000)