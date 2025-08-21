export const config = {
  apiUrl: process.env.NODE_ENV === 'production' 
    ? process.env.VITE_API_URL || 'https://your-app-name.railway.app'  // Replace with your actual Railway URL
    : 'http://localhost:8000'
};
