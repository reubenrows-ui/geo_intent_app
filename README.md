# Vertex AI Agent Engine Streamlit App

A complete Streamlit application that integrates with Google Cloud Vertex AI Agent Engine, providing a web interface for managing chat sessions and interacting with your deployed AI agent.

## Features

- 🤖 **Chat Interface**: Interactive chat with your Vertex AI Agent
- 📝 **Session Management**: Create, list, select, and delete chat sessions
- 🔄 **Real-time Updates**: Live conversation history with server-side context management
- 🔐 **Secure Authentication**: Service account-based authentication
- 📱 **Responsive UI**: Clean, modern interface built with Streamlit

## Prerequisites

1. **Google Cloud Project** with Vertex AI API enabled
2. **Service Account** with appropriate permissions:
   - Vertex AI User
   - Storage Admin (for staging bucket)
3. **Deployed Agent Engine** 

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Authentication

Create `.streamlit/secrets.toml` with your service account credentials:

```toml
[gcp_service_account]
type = "service_account"
project_id = "your-project-id"
private_key_id = "your-private-key-id"
private_key = "-----BEGIN PRIVATE KEY-----\nYOUR_PRIVATE_KEY\n-----END PRIVATE KEY-----\n"
client_email = "your-service-account@your-project.iam.gserviceaccount.com"
client_id = "your-client-id"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/robot/v1/metadata/x509/your-service-account%40your-project.iam.gserviceaccount.com"
client_x509_cert_url = "https://www.googleapis.com/robot/v1/metadata/x509/your-service-account%40your-project.iam.gserviceaccount.com"
universe_domain = "googleapis.com"
```

### 3. Deploy Your Agent

First, deploy your agent then copy the Resource ID from the output.

### 4. Update Configuration

Edit `app.py` and replace the placeholder with your actual Resource ID:

```python
# TODO: Replace with your actual resource ID from remote.py --create
RESOURCE_ID = "your-actual-resource-id-here"
```

### 5. Run the Application

```bash
streamlit run app.py
```

The app will be available at `http://localhost:8501`

## Usage

1. **Create a Session**: Click "Create New Session" in the sidebar
2. **Start Chatting**: Select a session and type your message in the chat input
3. **View History**: Conversation history is automatically displayed and managed server-side
4. **Manage Sessions**: Use the sidebar to switch between sessions or delete old ones


## Troubleshooting

### ImportError: No module named 'vertexai.agent_engines'

**Solution**: Install the correct version with agent_engines support:

```bash
pip install "google-cloud-aiplatform[adk,agent_engines]>=1.60.0"
pip install "google-adk>=1.4.2"
```

### Authentication Errors

**Solutions**:
1. Verify your service account has the correct permissions
2. Check that your `.streamlit/secrets.toml` file is properly formatted
3. Ensure your service account key is valid and not expired

### "Please update RESOURCE_ID" Error

**Solution**: 
1. Run `python remote.py --create` to deploy your agent
2. Copy the Resource ID from the output
3. Update the `RESOURCE_ID` variable in `app.py`

### Session Creation Fails

**Possible causes**:
1. Invalid Resource ID
2. Agent not properly deployed
3. Insufficient permissions

**Solutions**:
1. Verify the Resource ID is correct
2. Redeploy the agent: `python remote.py --create`
3. Check service account permissions

### No Response from Agent

**Possible causes**:
1. Agent deployment issues
2. Network connectivity problems
3. Invalid session ID

**Solutions**:
1. Check agent deployment status
2. Verify network connectivity to Google Cloud
3. Create a new session and try again

## File Structure

```
st_app/
├── app.py                 # Main Streamlit application
├── requirements.txt      # Python dependencies
├── README.md            # This file
├── .streamlit/
│   └── secrets.toml     # Authentication secrets
└── .venv/               # Python virtual environment
```

## Support

If you encounter issues:

1. Check the troubleshooting section above
2. Verify all prerequisites are met
3. Ensure your Google Cloud project has the necessary APIs enabled
4. Check the Streamlit logs for detailed error messages

## License

This project is licensed under the MIT License.
