import http from "k6/http";
import { check, sleep } from "k6";

export const options = {
  stages: [
    { duration: "10s", target: 10 }, // ramp up to 10 VUs
    { duration: "30s", target: 20 }, // hold at 20 VUs
    { duration: "2m", target: 50 }, // peak load
    { duration: "10s", target: 0 }, // ramp down
  ],
};

const BASE_URL = __ENV.BASE_URL || "http://localhost:8000";
const ACCESS_TOKEN = __ENV.ACCESS_TOKEN || "";

export default function () {
  const headers = {
    headers: {
      Authorization: `Bearer ${ACCESS_TOKEN}`,
      "Content-Type": "application/json",
    },
  };

  // 1️⃣ GET /api/orders/
  let resOrders = http.get(`${BASE_URL}/api/orders/`, headers);
  check(resOrders, {
    "orders list: status 200": (r) => r.status === 200,
  });

  // 2️⃣ If orders exist, GET detail of first one
  let orders = [];
  try {
    orders = resOrders.json();
  } catch (e) {
    // if response isn't JSON, fail gracefully
  }

  if (orders.length > 0) {
    let orderId = orders[0].id;
    let resDetail = http.get(`${BASE_URL}/api/orders/${orderId}/`, headers);
    check(resDetail, {
      "order detail: status 200": (r) => r.status === 200,
    });
  } else {
    check(null, {
      "order detail: skipped (no orders)": () => true,
    });
  }

  // 3️⃣ GET /api/users/auth/user/
  let resUser = http.get(`${BASE_URL}/api/users/auth/user/`, headers);
  check(resUser, {
    "user info: status 200": (r) => r.status === 200,
  });

  sleep(1); // pacing between iterations
}
