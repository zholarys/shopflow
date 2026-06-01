import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  stages: [
    { duration: '30s', target: 100 },
    { duration: '30s', target: 300 },
    { duration: '30s', target: 600 },
    { duration: '30s', target: 1000 },
    { duration: '30s', target: 0 },
  ],
  thresholds: {
    http_req_duration: ['p(95)<2000'],
    http_req_failed: ['rate<0.05'],
  },
};

const BASE_URL = 'http://localhost';

export default function () {
  const products = http.get(`${BASE_URL}/api/products/`);
  check(products, {
    'products status 200': (r) => r.status === 200,
    'products < 1000ms': (r) => r.timings.duration < 1000,
  });
  sleep(0.3);

  const health = http.get(`${BASE_URL}/api/health`);
  check(health, {
    'health status 200': (r) => r.status === 200,
  });
  sleep(0.3);
}
