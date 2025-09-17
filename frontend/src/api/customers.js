
const API_URL = process.env.REACT_APP_API_URL; 

async function base(path, { method = 'GET', body, headers = {}, token, withCredentials = false } = {}) {
  const res = await fetch(`${API_URL}${path}`, {
    method,
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...headers,
    },
    credentials: withCredentials ? 'include' : 'same-origin',
    body,
  });

  let data = null;
  try { data = await res.json(); } catch {  }

  if (!res.ok) {
    
    const msg = data?.message || `${res.status} ${res.statusText}`;
    throw new Error(msg);
  }
  return data;
}


/**
 * Creating a new customer 
 * @param {{name: string, email?: string, customerId?: string}} payload
 */

export function addCustomer({ name, email, customerId }) {

  if (customerId != null && customerId !== '' && !/^[0-9]{3,32}$/.test(String(customerId))) {
    throw new Error('Must contan 3-8 numbers');
  }
  return base('/customers', {
    method: 'POST',
    body: JSON.stringify({ name, email, customerId }),
  });
}

//Searching customer 
export async function searchCustomersByName(name) {
  const q = (name ?? '').trim();
  if (!q) return [];

  const data = await base(`/customers?name=${encodeURIComponent(q)}`);

  if (Array.isArray(data)) return data;
  if (Array.isArray(data?.results)) return data.results;
  return data ? [data] : [];
}