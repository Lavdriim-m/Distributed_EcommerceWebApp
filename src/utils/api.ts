import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:5000/api',
  timeout: 10000,
});

api.interceptors.response.use(
  response => response,
  async error => {
    const { config } = error;
    if (!config || !config.retry) {
      return Promise.reject(error);
    }

    config.retryCount = config.retryCount || 0;

    if (config.retryCount >= config.retry) {
      return Promise.reject(error);
    }

    config.retryCount += 1;
    const backoff = new Promise(resolve => {
      setTimeout(() => {
        resolve(null);
      }, config.retryDelay || 1000);
    });

    await backoff;
    return api(config);
  }
);

export default api; 