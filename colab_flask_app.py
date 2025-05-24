# --- YouTube View Counter Flask App for Google Colab ---

# Step 1: Install necessary packages
# Uncomment and run this line in a Colab cell if these packages are not already installed:
# !pip install Flask requests flask_ngrok

# Step 2: Import required libraries
from flask import Flask, request, jsonify # Flask for web app, request for query params, jsonify for JSON responses
import requests # To make HTTP requests to the YouTube API
from flask_ngrok import run_with_ngrok # To expose the Flask app via ngrok in Colab

# Step 3: Initialize Flask App and Configure ngrok
app = Flask(__name__) # Create a Flask application instance
run_with_ngrok(app)   # Wrap the app with ngrok to make it publicly accessible from Colab

# Step 4: Store YouTube API Key
# IMPORTANT: Replace with your actual YouTube Data API v3 key.
# Keep API keys secure and do not expose them publicly in production environments.
YOUTUBE_API_KEY = 'AIzaSyDtKcL9CLApLJJEaYyEIE9JDsj5VBDc1bs' # Hardcoded API Key

# Step 5: Define the HTML Template for the Frontend
# This HTML provides the user interface for entering a YouTube URL and seeing the view count.
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>YouTube Video View Counter (Colab)</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background-color: #f4f4f4; color: #333; }
        .container { background-color: #fff; padding: 20px; border-radius: 8px; box-shadow: 0 0 10px rgba(0,0,0,0.1); max-width: 500px; margin: auto; }
        h1 { color: #d32f2f; text-align: center; }
        input[type="text"] { width: calc(100% - 22px); padding: 10px; margin-bottom: 10px; border: 1px solid #ddd; border-radius: 4px; }
        button { background-color: #d32f2f; color: white; padding: 10px 15px; border: none; border-radius: 4px; cursor: pointer; width: 100%; }
        button:hover { background-color: #b71c1c; }
        #resultArea { margin-top: 15px; padding: 10px; border: 1px solid #eee; border-radius: 4px; background-color: #e9e9e9; min-height: 30px; }
        .error { color: red; font-weight: bold; }
        .success { color: green; font-weight: bold; }
    </style>
</head>
<body>
    <div class="container">
        <h1>YouTube Video View Counter (Colab)</h1>
        <input type="text" id="youtubeUrl" placeholder="Enter YouTube Video URL">
        <button id="getViewCountBtn">Get View Count</button>
        <div id="resultArea"></div>
    </div>

    <script>
        const urlInput = document.getElementById('youtubeUrl');
        const getViewsBtn = document.getElementById('getViewCountBtn');
        const resultArea = document.getElementById('resultArea');

        function extractVideoId(url) {
            let videoId = null;
            const regexes = [
                /(?:https?:\/\/)?(?:www\.)?youtube\.com\/watch\?v=([^&]+)/,
                /(?:https?:\/\/)?youtu\.be\/([^?]+)/,
                /(?:https?:\/\/)?(?:www\.)?youtube\.com\/embed\/([^?]+)/,
                /(?:https?:\/\/)?(?:www\.)?youtube\.com\/v\/([^?]+)/,
                /(?:https?:\/\/)?(?:www\.)?youtube\.com\/shorts\/([^?]+)/
            ];

            for (const regex of regexes) {
                const match = url.match(regex);
                if (match && match[1]) {
                    videoId = match[1];
                    break;
                }
            }
            if (videoId && /^[a-zA-Z0-9_-]{11}$/.test(videoId)) {
                return videoId;
            }
            return null;
        }

        getViewsBtn.addEventListener('click', async () => {
            resultArea.innerHTML = ''; // Clear previous results
            resultArea.className = ''; // Clear previous styling
            const url = urlInput.value.trim();

            if (!url) {
                resultArea.textContent = 'Please enter a YouTube video URL.';
                resultArea.className = 'error';
                return;
            }

            const videoId = extractVideoId(url);

            if (!videoId) {
                resultArea.textContent = 'Invalid YouTube URL or Video ID could not be extracted.';
                resultArea.className = 'error';
                return;
            }

            try {
                resultArea.textContent = 'Fetching view count...';
                // Use relative path for the API endpoint
                const response = await fetch(`/video-stats?videoId=${videoId}`); 
                
                const data = await response.json(); // Try to parse JSON regardless of response.ok

                if (response.ok) {
                    if (data.error) { // Backend might still send an error in a 200 response (though less common for this setup)
                        resultArea.textContent = `Error: ${data.error}`;
                        resultArea.className = 'error';
                    } else if (data.liveViewCount !== undefined) {
                        resultArea.textContent = `Live Viewers: ${data.liveViewCount.toLocaleString()}`;
                        resultArea.className = 'success';
                    } else if (data.totalViewCount !== undefined) {
                        resultArea.textContent = `Total Views: ${data.totalViewCount.toLocaleString()}`;
                        resultArea.className = 'success';
                    } else {
                        resultArea.textContent = 'Could not retrieve view count. The video may not have view statistics available or it might be a private video.';
                        resultArea.className = 'error';
                    }
                } else { // response.ok is false
                     resultArea.textContent = `Error: ${data.error || `Failed to fetch data from server (Status: ${response.status})`}`;
                     resultArea.className = 'error';
                }
            } catch (error) {
                console.error('Frontend fetch error:', error);
                resultArea.textContent = 'An error occurred while trying to fetch video statistics. Check console for details.';
                resultArea.className = 'error';
            }
        });
    </script>
</body>
</html>
"""

# Step 6: Define Flask Routes

# Route 1: Root URL ('/') - Serves the HTML Frontend
# This route renders the HTML page defined in HTML_TEMPLATE.
@app.route('/')
def home():
    """Serves the main HTML page."""
    return HTML_TEMPLATE, 200, {'Content-Type': 'text/html'}

# Route 2: API Endpoint ('/video-stats') - Fetches YouTube Video Statistics
# This endpoint takes a 'videoId' query parameter, calls the YouTube API,
# and returns live or total view count.
@app.route('/video-stats', methods=['GET'])
def video_stats():
    """Handles requests for video statistics."""
    video_id = request.args.get('videoId') # Get 'videoId' from query parameters

    # Validate videoId presence
    if not video_id:
        return jsonify(error='videoId query parameter is required'), 400

    # Construct the YouTube API URL
    youtube_api_url = f"https://www.googleapis.com/youtube/v3/videos?part=liveStreamingDetails%2Cstatistics&id={video_id}&key={YOUTUBE_API_KEY}"

    try:
        # Make the request to YouTube API
        response = requests.get(youtube_api_url)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)
        data = response.json()       # Parse JSON response

        # Check if video data is present
        if not data.get('items'):
            return jsonify(error='Video not found or API error (e.g., invalid video ID)'), 404

        video_details = data['items'][0]

        # Prioritize live view count if available
        live_streaming_details = video_details.get('liveStreamingDetails')
        if live_streaming_details and 'concurrentViewers' in live_streaming_details:
            return jsonify(liveViewCount=int(live_streaming_details['concurrentViewers']))
        
        # Fallback to total view count
        statistics = video_details.get('statistics')
        if statistics and 'viewCount' in statistics:
            return jsonify(totalViewCount=int(statistics['viewCount']))
        
        # If no view count information is found
        return jsonify(error='Could not retrieve view count. Video might be private, have stats disabled, or is not a standard video type.'), 500

    except requests.exceptions.HTTPError as http_err:
        # Handle specific HTTP errors from the YouTube API call
        error_details_from_youtube = {}
        try:
            error_details_from_youtube = response.json().get('error', {}) # YouTube often returns JSON error details
        except ValueError: # If response is not JSON
            pass
        
        status_code = response.status_code
        if status_code == 403:
             error_message = "Forbidden: Check your YouTube API key, ensure it's valid, and that the YouTube Data API v3 is enabled. Also, check quotas."
        elif status_code == 400:
            error_message = "Bad Request: Likely an invalid videoId format or issue with other parameters sent to YouTube API."
        else:
            error_message = f"YouTube API HTTP error: {http_err}"
        return jsonify(error=error_message, youtube_error_details=error_details_from_youtube), status_code
    
    except requests.exceptions.RequestException as req_err:
        # Handle network errors or other issues with the request itself
        return jsonify(error=f"Failed to fetch video statistics due to a network or request issue: {req_err}"), 503 # Service Unavailable
    
    except Exception as e:
        # Catch any other unexpected errors during the process
        return jsonify(error=f"An unexpected server error occurred: {str(e)}"), 500

# Step 7: Standard way to run Flask app (optional in Colab when cell is run)
# In a typical Python script, you would run the app using app.run().
# In Colab, running the cell that defines 'app' and 'run_with_ngrok(app)'
# is usually sufficient to start the server and get the ngrok URL.
# This block is included for completeness and if you were to run this script outside Colab.
if __name__ == '__main__':
    # This part is generally not executed directly when running a cell in Colab,
    # as run_with_ngrok() handles the app startup.
    # However, it's good practice for standalone Flask apps.
    app.run(debug=False) # debug=False is generally safer for public-facing ngrok tunnels

# --- How to Run in Google Colab ---
# 1. Create a new Colab Notebook.
# 2. Create a new code cell.
# 3. Copy and paste the ENTIRE content of this script into that single code cell.
# 4. IMPORTANT: If you haven't installed Flask, requests, or flask_ngrok in your Colab environment before,
#    uncomment the line `# !pip install Flask requests flask_ngrok` at the top of the script.
# 5. Run the cell.
# 6. After execution, ngrok will provide a public URL (usually ending in .ngrok.io).
#    Example output you'll see in the cell:
#    * Serving Flask app "colab_flask_app" (lazy loading)
#    * Environment: production
#      WARNING: This is a development server. Do not use it in a production deployment.
#      Use a production WSGI server instead.
#    * Debug mode: off
#    * Running on http://<some_hash>.ngrok.io
#    * Traffic stats available on http://127.0.0.1:4040
# 7. Click on the ngrok URL to open your running web application in a new browser tab.
# 8. Enter a YouTube video URL and click "Get View Count".
#
# Note on API Key: The provided YOUTUBE_API_KEY is a placeholder/example.
# You MUST replace it with your own valid YouTube Data API v3 key for the application to work.
# Ensure the YouTube Data API v3 is enabled for your key in the Google Cloud Console.
