# GeoBikunAlert

GeoBikunAlert is a Flask-based web application that tracks the real-time location of buses on the University of Indonesia campus. The application scrapes bus location data from the Bikun UI website and displays it on a map. When a bus is nearing a specified station, the application sends an email notification to alert users.

## Features

- Real-time bus tracking: The application scrapes the Bikun UI website every 10 seconds to get the latest bus locations.
- Proximity alerts: When a bus is within a certain distance of a specified station, the application sends an email notification.
- Map display: The application displays the bus locations on a map for easy visualization.

## How It Works

1. The application uses Selenium WebDriver to scrape the Bikun UI website for bus location data.
2. The scraped data is stored in a list and updated every 10 seconds.
3. The application calculates the distance between each bus and the specified station using the geodesic function from the geopy library.
4. If a bus is within the proximity threshold, the application sends an email notification. To prevent spamming, the application keeps track of which buses have already triggered a notification and only sends a new notification if the bus has moved out of the proximity threshold and then reentered it.

## Setup

1. Clone the repository.
2. Install the required Python packages using pip: `pip install -r requirements.txt`
3. Run the Flask application: `python app.py`
4. Open a web browser and go to `http://localhost:5000` to view the application.

## Dependencies

- Flask
- Selenium WebDriver
- geopy
- APScheduler
- smtplib

## Future Improvements

- Improve the scraping efficiency and accuracy.
- Add more detailed bus information, such as bus number and capacity.

## Contributing

Contributions are welcome!
