const express = require('express');
const fetch = require('node-fetch');

const app = express();
const PORT = process.env.PORT || 3000;

// Serve static files from the 'public' directory
app.use(express.static('public'));

app.get('/', (req, res) => {
  res.send('Hello World!');
});

// Endpoint to fetch YouTube video statistics
app.get('/video-stats', async (req, res) => {
  const { videoId } = req.query;
  const API_KEY = 'AIzaSyDtKcL9CLApLJJEaYyEIE9JDsj5VBDc1bs'; // Store API keys securely in a real application

  if (!videoId) {
    return res.status(400).json({ error: 'videoId query parameter is required' });
  }

  const YOUTUBE_API_URL = `https://www.googleapis.com/youtube/v3/videos?part=liveStreamingDetails%2Cstatistics&id=${videoId}&key=${API_KEY}`;

  try {
    const apiResponse = await fetch(YOUTUBE_API_URL);
    const data = await apiResponse.json();

    // Check if the API returned any items (videos)
    if (!data.items || data.items.length === 0) {
      return res.status(404).json({ error: 'Video not found or API error' });
    }

    const videoDetails = data.items[0];

    // Check for live streaming details and concurrent viewers
    if (videoDetails.liveStreamingDetails && videoDetails.liveStreamingDetails.concurrentViewers) {
      return res.json({ liveViewCount: parseInt(videoDetails.liveStreamingDetails.concurrentViewers, 10) });
    } 
    // Otherwise, return total view count from statistics
    else if (videoDetails.statistics && videoDetails.statistics.viewCount) {
      return res.json({ totalViewCount: parseInt(videoDetails.statistics.viewCount, 10) });
    } 
    // If neither is available, it's an unexpected response format or the video has no stats
    else {
      return res.status(500).json({ error: 'Could not retrieve view count for the video' });
    }

  } catch (error) {
    console.error('Error fetching video stats:', error);
    return res.status(500).json({ error: 'Failed to fetch video statistics' });
  }
});

app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});
