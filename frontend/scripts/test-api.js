const axios = require('axios');

const API_KEY = 'sk-28c643380ebc43fdb85cd08d7f53ae25';
const API_URL = 'https://api.openai.com/v1/images/generations';

async function test() {
  try {
    const response = await axios.post(
      API_URL,
      {
        model: 'dall-e-3',
        prompt: 'a simple test image of a red apple',
        n: 1,
        size: '1024x1024',
        quality: 'standard',
        style: 'natural'
      },
      {
        headers: {
          'Authorization': `Bearer ${API_KEY}`,
          'Content-Type': 'application/json'
        }
      }
    );
    console.log('Success! Response:', JSON.stringify(response.data, null, 2));
  } catch (error) {
    console.error('Error:', error.message);
    if (error.response) {
      console.error('Status:', error.response.status);
      console.error('Data:', JSON.stringify(error.response.data, null, 2));
    }
  }
}

test();