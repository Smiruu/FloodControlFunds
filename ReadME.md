**Flood Prediction System – Technical Summary**

**Overview**

The Flood Prediction System is a web-based application that utilizes machine learning and real-time weather data to forecast potential flood risks. By integrating meteorological data from the Open-Meteo API with unsupervised learning algorithms—Isolation Forest and K-Means Clustering—the system analyzes environmental conditions to identify early signs of possible flooding.

The project aims to improve disaster preparedness by providing accurate, real-time flood risk insights that help communities and local authorities make informed decisions.

**System Architecture**

The Flood Prediction System follows a client–server architecture, composed of a Flask backend for processing and prediction, and a React (Vite) frontend for visualization.

1. Frontend (React + Vite, deployed on Vercel)

    The frontend serves as the interactive interface through which users access live weather data and flood predictions.

    * Framework: Built using ReactJS, with Vite for fast development, optimized builds, and efficient hot reloading.

    * User Interface: Designed to be responsive, clean, and intuitive, displaying temperature, rainfall, humidity, and wind speed alongside flood risk levels.

    * API Communication: Fetches prediction results from the Flask backend via RESTful API requests.

    * Visualization: Data and model predictions are dynamically rendered, ensuring users receive real-time updates with every request.

2. Backend (Flask, deployed on Render)

    The backend handles the application’s data processing, API integration, and machine learning model execution.

    * API Integration: Connects to the Open-Meteo API to retrieve real-time weather parameters, including rainfall, temperature, and wind speed.

    * Preprocessing: Collected data is normalized and transformed into numerical features suitable for model inference.

    * Model Execution: Executes the Isolation Forest and K-Means models to analyze data and determine the corresponding flood risk category.

    * API Endpoint: Sends the prediction results back to the frontend in JSON format for visualization.

**Machine Learning Models**

Two unsupervised learning models form the core of the system’s predictive intelligence:

  Isolation Forest: Detects anomalous weather patterns, such as unusually high rainfall or abrupt temperature changes that may indicate flood conditions.

  K-Means Clustering: Groups meteorological data into distinct risk categories (Low, Moderate, High). New weather data is classified into one of these clusters to represent the current flood risk level.

  Both models are trained using historical and synthetic weather datasets to identify patterns strongly correlated with flood events.

**Data Flow**

  The React frontend sends a request to the Flask API.

  Flask retrieves real-time data from the Open-Meteo API.

  Data is preprocessed and analyzed by the Isolation Forest and K-Means models.

  The models output a flood risk level.

  Flask returns the prediction to React, which displays it to the user.

**Deployment**

Backend: Deployed on Render, providing a stable Python environment for the Flask API and model execution.

Frontend: Deployed on Vercel, ensuring fast load times and global accessibility.

No Database: The system operates without a database, relying entirely on real-time data from the Open-Meteo API and local model inference.
