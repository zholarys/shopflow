import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  stages: [
    { duration: '30s', target: 10 },
    { duration: '30s', target: 50 },
    { duration: '30s', target: 100 },
    { duration: '30s', target: 0 },
  ],
  thresholds: {
    http_req_duration: ['p(95)<500'],
    http_req_failed: ['rate<0.01'],
  },
};

const BASE_URL = 'http://localhost';

export default function () {
  const products = http.get(`${BASE_URL}/api/products/`);
  check(products, {
    'products status 200': (r) => r.status === 200,
    'products response time < 200ms': (r) => r.timings.duration < 200,
  });
  sleep(0.5);

  const health = http.get(`${BASE_URL}/api/health`);
  check(health, {
    'health status 200': (r) => r.status === 200,
  });
  sleep(0.5);

  const categories = http.get(`${BASE_URL}/api/products/categories`);
  check(categories, {
    'categories status 200': (r) => r.status === 200,
  });
  sleep(1);
}
