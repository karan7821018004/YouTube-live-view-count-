# YouTube Live View Counter

A simple web application to display the live (or total) view count for a YouTube video.

## Prerequisites

- Node.js and npm installed.

## Setup and Running the Application

1.  **Clone the repository (or download the files).**
2.  **Navigate to the `express_project` directory:**
    ```bash
    cd express_project
    ```
3.  **Install dependencies:**
    ```bash
    npm install
    ```
4.  **API Key:**
    This application requires a YouTube Data API v3 key. The key `AIzaSyDtKcL9CLApLJJEaYyEIE9JDsj5VBDc1bs` has been hardcoded into `index.js` for simplicity in this example. For a production application, you would typically store this in an environment variable or a configuration file.

5.  **Start the server:**
    ```bash
    node index.js
    ```
6.  **Open your browser:**
    Navigate to `http://localhost:3000`.

## How to Use

1.  Enter a YouTube video URL into the input field.
2.  Click the "Get View Count" button.
3.  The live view count (if the video is currently live) or the total view count will be displayed.
