export const config = {
  apiUrl: process.env.NODE_ENV === 'production' 
    ? process.env.VITE_API_URL || 'https://your-backend-url.railway.app'  // Set this in Vercel environment variables
    : 'http://localhost:8000'
};
