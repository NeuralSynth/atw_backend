# k6 Load Test Script for ATW Backend

import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate, Trend, Counter } from 'k6/metrics';

// Custom metrics
const errorRate = new Rate('errors');
const responseTime = new Trend('response_time');
const requestCount = new Counter('requests');

// Test configuration
export const options = {
  stages: [
    // Ramp-up to 1K req/sec
    { duration: '2m', target: 1000 },
    
    // Hold at 1K req/sec
    { duration: '5m', target: 1000 },
    
    // Ramp-up to 10K req/sec
    { duration: '3m', target: 10000 },
    
    // Hold at 10K req/sec
    { duration: '10m', target: 10000 },
    
    // Ramp-up to 100K req/sec
    { duration: '5m', target: 100000 },
    
    // Hold at 100K req/sec
    { duration: '15m', target: 100000 },
    
    // Ramp-up to 1M req/sec (EXTREME - requires distributed testing)
    // { duration: '10m', target: 1000000 },
    
    // Ramp-down
    { duration: '5m', target: 0 },
  ],
  
  thresholds: {
    http_req_duration: ['p(95)<200', 'p(99)<500'],  // 95% < 200ms, 99% < 500ms
    http_req_failed: ['rate<0.01'],  // Error rate < 1%
    errors: ['rate<0.01'],
  },
};

const BASE_URL = __ENV.BASE_URL || 'https://api.atw.com';

// Test scenarios
export default function () {
  const endpoints = [
    { method: 'GET', path: '/api/v1/trips/', weight: 40 },
    { method: 'GET', path: '/api/v1/vehicles/', weight: 20 },
    { method: 'GET', path: '/api/v1/patients/', weight: 15 },
    { method: 'GET', path: '/api/v1/users/', weight: 10 },
    { method: 'POST', path: '/api/v1/trips/', weight: 10 },
    { method: 'GET', path: '/api/v1/billing/', weight: 5 },
  ];
  
  // Weighted random selection
  const rand = Math.random() * 100;
  let cumulative = 0;
  let selectedEndpoint = endpoints[0];
  
  for (const endpoint of endpoints) {
    cumulative += endpoint.weight;
    if (rand < cumulative) {
      selectedEndpoint = endpoint;
      break;
    }
  }
  
  const url = `${BASE_URL}${selectedEndpoint.path}`;
  const params = {
    headers: {
      'Content-Type': 'application/json',
      // Add authentication if needed
      // 'Authorization': 'Bearer ' + __ENV.API_TOKEN,
    },
    tags: { name: selectedEndpoint.path },
  };
  
  let response;
  const startTime = new Date();
  
  if (selectedEndpoint.method === 'GET') {
    response = http.get(url, params);
  } else if (selectedEndpoint.method === 'POST') {
    const payload = JSON.stringify({
      // Add appropriate payload
      test: true,
    });
    response = http.post(url, payload, params);
  }
  
  const duration = new Date() - startTime;
  
  // Record metrics
  requestCount.add(1);
  responseTime.add(duration);
  
  // Checks
  const result = check(response, {
    'status is 200-299': (r) => r.status >= 200 && r.status < 300,
    'response time < 200ms': (r) => r.timings.duration < 200,
    'response time < 500ms': (r) => r.timings.duration < 500,
    'has body': (r) => r.body && r.body.length > 0,
  });
  
  if (!result) {
    errorRate.add(1);
  }
  
  // Small sleep to avoid overwhelming (adjust based on target RPS)
  sleep(0.01);
}

export function handleSummary(data) {
  return {
    'summary.json': JSON.stringify(data),
    stdout: textSummary(data, { indent: ' ', enableColors: true }),
  };
}

function textSummary(data, options) {
  const indent = options.indent || '';
  const colors = options.enableColors || false;
  
  return `
${indent}Test Summary
${indent}============
${indent}Total Requests: ${data.metrics.requests.values.count}
${indent}Error Rate: ${(data.metrics.errors.values.rate * 100).toFixed(2)}%
${indent}Response Time (p95): ${data.metrics.http_req_duration.values['p(95)'].toFixed(2)}ms
${indent}Response Time (p99): ${data.metrics.http_req_duration.values['p(99)'].toFixed(2)}ms
${indent}Throughput: ${(data.metrics.http_reqs.values.rate).toFixed(2)} req/s
  `;
}
