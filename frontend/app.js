const express = require('express');
const axios = require('axios');
const path = require('path');

const app = express();

// Fix #2: API URL from environment
const API_URL = process.env.API_URL || 'http://api:8000';
const PORT = process.env.PORT || 3000;

app.use(express.json());
app.use(express.static(path.join(__dirname, 'views')));

// Fix #3: Health check endpoint
app.get('/health', (req, res) => {
  res.json({ status: 'healthy' });
});

app.post('/submit', async (req, res) => {
  try {
    const response = await axios.post(`${API_URL}/jobs`);
    res.json(response.data);
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: "Failed to submit job" });
  }
});

app.get('/status/:id', async (req, res) => {
  try {
    const response = await axios.get(`${API_URL}/jobs/${req.params.id}`);
    res.json(response.data);
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: "Failed to fetch job status" });
  }
});

app.listen(PORT, () => {
  console.log(`Frontend running on port ${PORT}`);
});
