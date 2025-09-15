import React, { useState } from "react";
import { changePassword } from "../api/password";
import "./ChangePassword.css";

function ChangePassword() {
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [message, setMessage] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const isPasswordValid = (password) => {
    const regex =
      /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*()_\-+=<>?{}\[\]~])[A-Za-z\d!@#$%^&*()_\-+=<>?{}\[\]~]{10,}$/;
    return regex.test(password);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setMessage("");

    if (!isPasswordValid(newPassword)) {
      setMessage(
        "Password must be at least 10 characters long and include uppercase, lowercase, number, and special character."
      );
      return;
    }
    if (newPassword !== confirmPassword) {
      setMessage("Passwords do not match.");
      return;
    }

    try {
      setSubmitting(true);
      await changePassword(newPassword);
      setMessage("Password changed successfully.");
      setNewPassword("");
      setConfirmPassword("");
    } catch (e) {
      setMessage(e.message || "Failed to change password.");
    } finally {
      setSubmitting(false);
    }
  };

  const invalidNew = newPassword && !isPasswordValid(newPassword);
  const success = /successfully/i.test(message);

  return (
    <main className="page">
      <section className="card form-card">
        <h1 className="card__title">Change Password</h1>
        <p className="card__subtitle">
          Use a strong password: at least 10 chars, with upper/lowercase, number, special.
        </p>

        <form className="form" onSubmit={handleSubmit} noValidate>
          <div className="field">
            <label className="field__label" htmlFor="new-password">New password</label>
            <input
              id="new-password"
              className={`field__input ${invalidNew ? "field__input--invalid" : ""}`}
              type="password"
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
              autoComplete="new-password"
              required
            />
            <small className="field__hint">
              10+ chars, upper/lowercase, number, special.
            </small>
          </div>

          <div className="field">
            <label className="field__label" htmlFor="confirm-password">Confirm password</label>
            <input
              id="confirm-password"
              className="field__input"
              type="password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              autoComplete="new-password"
              required
            />
          </div>

          <button className="btn btn--primary" type="submit" disabled={submitting}>
            {submitting ? "Saving..." : "Change Password"}
          </button>

          {message && (
            <p
              className={`notice ${success ? "notice--success" : "notice--error"}`}
              aria-live="polite"
            >
              {message}
            </p>
          )}
        </form>
      </section>
    </main>
  );
}

export default ChangePassword;
