import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate, Trend } from 'k6/metrics';

// Custom metrics
const errorRate = new Rate('errors');
const taskCreationTrend = new Trend('task_creation_duration');

// Test configuration
export const options = {
  stages: [
    { duration: '1m', target: 10 },   // Ramp up to 10 users
    { duration: '3m', target: 50 },   // Ramp up to 50 users
    { duration: '5m', target: 50 },   // Stay at 50 users
    { duration: '2m', target: 100 },  // Ramp up to 100 users
    { duration: '3m', target: 100 },  // Stay at 100 users
    { duration: '2m', target: 0 },    // Ramp down
  ],
  thresholds: {
    http_req_duration: ['p(95)<500', 'p(99)<1000'],
    errors: ['rate<0.01'],
    task_creation_duration: ['p(95)<300'],
  },
};

const BASE_URL = __ENV.BASE_URL || 'http://localhost:8000';
const API_KEY = __ENV.API_KEY || 'test-key';

const headers = {
  'Content-Type': 'application/json',
  'X-API-Key': API_KEY,
};

export default function () {
  // Health check
  const healthRes = http.get(`${BASE_URL}/health`);
  check(healthRes, {
    'health check status is 200': (r) => r.status === 200,
  });

  // List agents
  const agentsRes = http.get(`${BASE_URL}/api/v1/agents`, { headers });
  check(agentsRes, {
    'list agents status is 200': (r) => r.status === 200,
  });
  errorRate.add(agentsRes.status !== 200);

  // Create task
  const taskPayload = JSON.stringify({
    title: `Load test task ${Date.now()}`,
    description: 'Created during load testing',
    priority: 'P2',
    status: 'backlog',
  });

  const startTime = Date.now();
  const createRes = http.post(`${BASE_URL}/api/v1/tasks`, taskPayload, { headers });
  taskCreationTrend.add(Date.now() - startTime);

  const taskCreated = check(createRes, {
    'create task status is 201': (r) => r.status === 201,
  });
  errorRate.add(!taskCreated);

  if (taskCreated) {
    const task = JSON.parse(createRes.body);
    
    // Get task
    const getRes = http.get(`${BASE_URL}/api/v1/tasks/${task.id}`, { headers });
    check(getRes, {
      'get task status is 200': (r) => r.status === 200,
    });

    // Update task
    const updatePayload = JSON.stringify({ status: 'in_progress' });
    const updateRes = http.patch(`${BASE_URL}/api/v1/tasks/${task.id}`, updatePayload, { headers });
    check(updateRes, {
      'update task status is 200': (r) => r.status === 200,
    });

    // Delete task (cleanup)
    http.del(`${BASE_URL}/api/v1/tasks/${task.id}`, null, { headers });
  }

  sleep(1);
}

export function handleSummary(data) {
  return {
    'stdout': textSummary(data, { indent: ' ', enableColors: true }),
    'load-test-results.json': JSON.stringify(data, null, 2),
  };
}

function textSummary(data, options) {
  // Simple text summary
  const metrics = data.metrics;
  return `
Load Test Results
=================
Duration: ${data.state.testRunDurationMs}ms
VUs Max: ${metrics.vus_max?.values?.max || 0}

HTTP Requests:
  Total: ${metrics.http_reqs?.values?.count || 0}
  Rate: ${metrics.http_reqs?.values?.rate?.toFixed(2) || 0}/s

Response Times:
  Avg: ${metrics.http_req_duration?.values?.avg?.toFixed(2) || 0}ms
  P95: ${metrics.http_req_duration?.values['p(95)']?.toFixed(2) || 0}ms
  P99: ${metrics.http_req_duration?.values['p(99)']?.toFixed(2) || 0}ms

Errors: ${(metrics.errors?.values?.rate * 100)?.toFixed(2) || 0}%
`;
}
