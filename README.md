# Geo-Intent Agent Streamlit App

A Proof of Concept Streamlit application demonstrating an agent-driven framework for location intelligence. This app integrates with Google Cloud Vertex AI Agent Engine to provide a web interface for researching new business locations.

**Use Case:** Researching a new coffee shop location in the United States.

## Features

- 🤖 **Conversational AI**: Interact with a Vertex AI Agent trained for geospatial analysis.
- 📈 **Location Intelligence**: Ask questions about demographics, competition, and underserved areas.
- 📝 **Session Management**: Create, list, select, and delete chat sessions.
- 🔄 **Real-time Updates**: Live conversation history with server-side context management.
- 🔐 **Secure Authentication**: Uses Google Cloud service account credentials stored in Streamlit secrets.
- 📱 **Responsive UI**: Clean, modern interface built with Streamlit.

## Prerequisites

1.  **Google Cloud Project** with the Vertex AI API enabled.
2.  **Service Account** with the following roles:
    *   `Vertex AI User`
    *   `Storage Admin` (for the staging bucket)
3.  **A Deployed Agent Engine** on Vertex AI.

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Secrets

Create a file at `.streamlit/secrets.toml` and populate it with your Google Cloud credentials and Agent Engine Resource ID. You can use `.streamlit/secrets.toml.sample` as a template.

```toml
# .streamlit/secrets.toml

[gcp]
project_id = "your-gcp-project-id"
location = "us-central1"
resource_id = "your-agent-engine-resource-id" # <-- Add your Resource ID here

[gcp_service_account]
type = "service_account"
project_id = "your-gcp-project-id"
private_key_id = "your-private-key-id"
private_key = "-----BEGIN PRIVATE KEY-----\nYOUR_PRIVATE_KEY\n-----END PRIVATE KEY-----\n"
client_email = "your-service-account@your-project.iam.gserviceaccount.com"
client_id = "your-client-id"
# ... other service account fields
```

### 3. Run the Application

```bash
streamlit run app.py
```

The app will be available at `http://localhost:8501`.

## Usage

The application is designed for researching potential new coffee shop locations.

1.  **Start a Chat**: Click "Start New Chat" in the sidebar to begin a new research session.
2.  **Ask Questions**: Interact with the agent to gather intelligence. For example:
    *   **Demographics**: *"What is the median household income in downtown San Francisco?"*
    *   **Competition**: *"Find all coffee shops within a 1-mile radius of the Ferry Building in San Francisco."*
    *   **Underserved Areas**: *"Which zip codes in Brooklyn have a high population density but fewer than 3 coffee shops?"*
    *   **Reporting**: *"Generate a full location intelligence report for Seattle, Washington."*
3.  **Manage Sessions**: Use the sidebar to switch between different research sessions or delete old ones.

## Troubleshooting

### Authentication Errors or Missing Secrets
**Solution**:
1.  Ensure your `.streamlit/secrets.toml` file is correctly located and formatted.
2.  Verify your service account has the required permissions (`Vertex AI User`, `Storage Admin`).
3.  Check that your service account key details in `secrets.toml` are correct and the key has not expired.

### "Error fetching sessions" or "Could not load session details"
**Possible Causes**:
1.  The `resource_id` in `.streamlit/secrets.toml` is incorrect.
2.  The Agent Engine is not deployed correctly or is in an error state.
3.  Your service account lacks permissions to access the Agent Engine.

**Solutions**:
1.  Verify the `resource_id` in your secrets file matches the one from your Vertex AI deployment.
2.  Check the status of your Agent Engine in the Google Cloud Console.
3.  Confirm the service account permissions in IAM.

## File Structure

```
geo-intent-app/
├── app.py                 # Main Streamlit application
├── requirements.txt       # Python dependencies
├── README.md              # This file
├── .streamlit/
│   ├── secrets.toml       # Authentication secrets (DO NOT COMMIT)
│   └── secrets.toml.sample# Sample secrets file
└── .venv/                 # Python virtual environment
```
