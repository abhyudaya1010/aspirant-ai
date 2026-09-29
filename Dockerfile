# Use official lightweight Python image
FROM python:3.10-slim

# Set working directory inside the container
WORKDIR /app

# Install system dependencies required for certain python packages
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file first to leverage Docker caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose the port Streamlit runs on
EXPOSE 8501

# Configure Streamlit to run headlessly for container deployment
RUN mkdir -p ~/.streamlit
RUN echo "\
[server]\n\
headless = true\n\
address = '0.0.0.0'\n\
port = 8501\n\
" > ~/.streamlit/config.toml

# Command to run the Streamlit app
ENTRYPOINT ["streamlit", "run", "app.py"]
