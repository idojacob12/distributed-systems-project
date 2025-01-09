
# Distributed Systems Project

## Overview

This project is a distributed Cloud-Edge-IoT surveillance system designed to detect unknown individuals in images captured over time. The system integrates IoT devices, edge computing, and cloud analysis to create an efficient and scalable surveillance architecture. 

## Features

- **IoT Integration**: Simulates real-world cameras for image/frame capture from WISENET videos.
- **Edge Processing**: Pre-processes images to perform lightweight person detection using YOLO real-time object detection model.
- **Cloud Analysis**: Event-driven computation via AWS Lambda and image analysis using AWS Rekognition.
- **Scalable Design**: Designed to handle multiple IoT cameras and edge devices via Docker. 

## Technologies Used

- **Programming Language**: Python
- **Object Detection**: YOLO (You Only Look Once) model
- **Cloud Services**: AWS Lambda, AWS Rekognition
- **Containerization**: Docker

## System Architecture

### Layers
1. **IoT Layer**: Captures images using cameras and sends them to the edge layer.
2. **Edge Layer**: Processes images to detect persons and forwards relevant ones to the cloud.
3. **Cloud Layer**: Analyzes images to identify known and unknown individuals, triggering alerts as needed.

## Setup Instructions

1. **Clone the Repository**:

   ```bash
   git clone <repository-url>
   cd distributed-systems-project
   ```

2. **Install WiseNET Video Datasets**

   - Ensure that the WiseNET video datasets are downloaded and stored locally on the root of this project. These videos will be used for simulating the IoT cameras.

2. **Set Up Environment Variables**:

   - Create or adjust existing `.env` file in the root directory.
   - Define necessary environment variables based on the installed video datasets and Docker Compose setup. Adjust paths and settings to match your environment.

3. **Build and Run the Containers**:

   - Ensure Docker and Docker Compose are installed.
   - Start the services:
     ```bash
     docker-compose up --build
     ```

## Authors

- [Ido Jacob](https://github.com/idojacob12)
- [Gwehenberger Victor](https://github.com/realMiyagi)
- [Changseok Woo]()

## Acknowledgments

- **University of Innsbruck**: Distributed Systems group
- **Instructors**: Juan Aznar Poveda, Stefan Pedratscher, Marlon Etheredge