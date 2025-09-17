// src/api/api.js
// Base URL from .env (CRA) with safe fallback
const API_URL = (process.env.REACT_APP_API_URL || "http://localhost:8000").replace(/\/+$/, "");

// Small helper for requests with JSON and consistent error handling
async function request(path, { method = "GET", headers = {}, body } = {}) {
    const res = await fetch(`${API_URL}${path}`, {
        method,
        headers: { "Content-Type": "application/json", ...headers },
        body: body ? JSON.stringify(body) : undefined,
    });

    // Try to extract error details if not ok
    if (!res.ok) {
        let msg = `HTTP ${res.status}`;
        try {
            const err = await res.json();
            msg = err?.detail || err?.message || msg;
        } catch (_) { /* ignore */ }
        throw new Error(msg);
    }

    // Some endpoints may return no content
    if (res.status === 204) return null;

    // Default assume JSON
    return res.json();
}

/* ---------- Health ---------- */
export function healthz() {
    return request("/healthz");
}

/* ---------- Customers (בקאפי שקיים היום) ---------- */
export async function getCustomers({ limit = 50, offset = 0 } = {}) {
    const data = await request(`/customers?limit=${limit}&offset=${offset}`);
    // תומך גם במבנה {"items":[...],"count":N} וגם {"items":[]}
    return {
        items: Array.isArray(data) ? data : (data.items ?? []),
        count: typeof data?.count === "number" ? data.count : (Array.isArray(data) ? data.length : 0),
    };
}

export function createCustomer({ full_name, sector, package_name, notes }) {
    return request("/customers", {
        method: "POST",
        body: { full_name, sector, package_name, notes },
    });
}

/* ---------- Auth (עדיין לא ממומש בבאקאנד) ----------
   משאירים את הפונקציות עם אותו API כדי שהפרונט יתקמפל;
   הן ייזרקו שגיאה ברורה עד שנוסיף ראוטים אמיתיים בבאק. */

export async function loginUser(_credentials) {
    throw new Error("loginUser: endpoint not implemented yet on backend");
}

export async function registerUser(_userData) {
    throw new Error("registerUser: endpoint not implemented yet on backend");
}

export async function getProfile(_token) {
    throw new Error("getProfile: endpoint not implemented yet on backend");
}

export async function logoutUser(_token) {
    throw new Error("logoutUser: endpoint not implemented yet on backend");
}
