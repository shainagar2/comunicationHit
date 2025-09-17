import React, { useState } from "react";

import { addCustomer, searchCustomersByName } from "../api/customers";
import "../Dashboard.css";







function Dashboard(){

  // Add form
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [customerId, setCustomerId] = useState("");
  const [adding, setAdding] = useState(false);

  // Search form
  const [searchName, setSearchName] = useState("");
  const [searching, setSearching] = useState(false);
  const [results, setResults] = useState([]);

  // UI messages
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  // Validations
  const nameRegex = /^[\p{L}\s'-]{2,30}$/u;
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  const idRegex = /^\d{3,8}$/;

  //Add customer 
  const handleAddCustomer = async (e) => {
    e.preventDefault();
    setMessage("");
    setError("");

    if (!nameRegex.test(name)) {
      setError("name must be 2–30 letters and may include spaces, ' or -");
      return;
    }
    if (email && !emailRegex.test(email)) {
      setError("Email is invalid");
      return;
    }
    if (customerId && !idRegex.test(customerId)) {
      setError("Customer ID must be 3–8 digits (numbers only)");
      return;
    }

    setAdding(true);
    try {
      const created = await addCustomer({ name, email, customerId });
      setMessage(`new customer was created: ${created?.name ?? name}`);
      setName("");
      setEmail("");
      setCustomerId("");
    } catch (err) {
      setError(err.message || "Something went wrong");
    } finally {
      setAdding(false);
    }
  };

  // Search by name 
  const handleSearch = async (e) => {
    e.preventDefault();
    setMessage("");
    setError("");
    setResults([]);

    const q = searchName.trim();
    if (!q) {
      setMessage("type a name to search");
      return;
    }

    setSearching(true);
    try {
      const list = await searchCustomersByName(q);
      setResults(list);
      if (list.length === 0) setMessage("no customers were found");
    } catch (err) {
      setError(err.message || "Search failed");
    } finally {
      setSearching(false);
    }
  };

  return (
    <main className="page">
      <header className="page__header">
        <h1 className="page__title">Customers</h1>
        <p className="page__subtitle">Add a new customer quickly</p>
      </header>

    <section className="card">
        <h2 className="card__title">Add Customer</h2>
        <form className="form" onSubmit={handleAddCustomer} noValidate>
          <div className="field">
            <label className="field__label" htmlFor="customer-name">customer name:</label>
            <input
              id="customer-name"
              className="field__input"
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="e.g., Simcha Rif"
              required
            />
            <small className="field__hint">2–30 letters, spaces allowed</small>
          </div>

          <div className="field">
            <label className="field__label" htmlFor="customer-email">email (optional):</label>
            <input
              id="customer-email"
              className="field__input"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="name@example.com"
            />
          </div>

          <div className="field">
            <label className="field__label" htmlFor="customer-id">Customer ID (digits only, optional):</label>
            <input
              id="customer-id"
              className="field__input"
              type="text"
              value={customerId}
              onChange={(e) => {
                
                const digitsOnly = e.target.value.replace(/\D/g, "").slice(0, 8);
                setCustomerId(digitsOnly);
              }}
              inputMode="numeric"
              placeholder="e.g., 00123456"
            />
          </div>

          <button className="btn btn--primary" type="submit" disabled={adding}>
            {adding ? "saving..." : "add Customer"}
          </button>

          {error && <p className="notice" style={{ color: "crimson" }}>{error}</p>}
          {message && <p className="notice notice--success">{message}</p>}
        </form>
      </section>

      <section className="card" style={{ marginTop: 16 }}>
        <h2 className="card__title">Search Customer</h2>
        <form className="form" onSubmit={handleSearch}>
          <div className="field">
            <label className="field__label" htmlFor="search-name">search by name:</label>
            <input
              id="search-name"
              className="field__input"
              type="text"
              value={searchName}
              onChange={(e) => setSearchName(e.target.value)}
              placeholder="type a name…"
            />
          </div>
          <button className="btn" type="submit" disabled={searching}>
            {searching ? "searching..." : "search"}
          </button>
        </form>

        {results.length > 0 && (
           <div style={{ overflowX: "auto", marginTop: 12 }}>
    <table className="table">
      <thead>
        <tr>
          <th style={{ textAlign: "left" }}>#</th>
          <th style={{ textAlign: "left" }}>Name</th>
          <th style={{ textAlign: "left" }}>Email</th>
          <th style={{ textAlign: "left" }}>ID</th>
        </tr>
      </thead>
      <tbody>
        {results.map((c, i) => {
          const id = c.customerId ?? c.id ?? c._id ?? i;
          return (
            <tr key={String(id)}>
              <td>{i + 1}</td>
              <td>{c.name ?? c.username ?? "—"}</td>
              <td>{c.email ?? "—"}</td>
              <td>{c.customerId ?? c.id ?? c._id ?? "—"}</td>
            </tr>
          );
        })}
      </tbody>
    </table>
  </div>)}
      </section> 
    </main>
  );
}


export default Dashboard;