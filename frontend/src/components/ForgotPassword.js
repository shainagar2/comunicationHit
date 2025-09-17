import { useState } from "react";
import { useNavigate } from "react-router-dom";
import "./ForgotPassword.css";

function ForgotPassword() {
  const [email, setEmail] = useState("");
  const [codeSent, setCodeSent] = useState(false);
  const [code, setCode] = useState("");
  const [msg, setMsg] = useState("");
  const [sending, setSending] = useState(false);
  const [verifying, setVerifying] = useState(false);

  const navigate = useNavigate();

  const isEmailValid = (val) => /\S+@\S+\.\S+/.test(val);

  // send code to the server
  const handleSendCode = async (e) => {
    e.preventDefault();
    setMsg("");

    if (!isEmailValid(email)) {
      setMsg("Please enter a valid email address.");
      return;
    }

    try {
      setSending(true);
      const response = await fetch("http://localhost:5000/api/forgot-password", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email }),
      });

      const data = await response.json().catch(() => ({}));
      if (response.ok) {
        setCodeSent(true);
        setMsg(data?.message || "If the email exists, we've sent a reset code.");
      } else {
        setMsg(data?.message || "We couldn't send a code. Please try again.");
      }
    } catch {
      setMsg("Network error. Please try again.");
    } finally {
      setSending(false);
    }
  };

  // verify the code that the user got
  const handleVerifyCode = async () => {
    setMsg("");

    if (!code.trim()) {
      setMsg("Please enter the verification code.");
      return;
    }

    try {
      setVerifying(true);
      const response = await fetch("http://localhost:5000/api/verify-code", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, code }),
      });

      const data = await response.json().catch(() => ({}));
      if (response.ok && data?.success) {
        // Pass token (the code) forward so you won't ask for it again
        navigate("/changepassword", { state: { email, token: code } });
      } else {
        setMsg(data?.message || "Incorrect or expired code.");
      }
    } catch {
      setMsg("Network error. Please try again.");
    } finally {
      setVerifying(false);
    }
  };

  // consider it "success style" when message sounds positive
  const success = /(sent|success|email)/i.test(msg);

  return (
    <main className="page">
      <section className="card">
        <h1 className="card__title">Forgot Password</h1>
        <p className="card__subtitle">
          Enter your email to receive a verification code, then verify it to continue to change your password.
        </p>

        {!codeSent && (
          <form className="form" onSubmit={handleSendCode} noValidate>
            <div className="field">
              <label className="field__label" htmlFor="email">Email address</label>
              <input
                id="email"
                className={`field__input ${
                  email && !isEmailValid(email) ? "field__input--invalid" : ""
                }`}
                type="email"
                placeholder="name@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                autoComplete="email"
                required
              />
            </div>

            <button className="btn btn--primary" type="submit" disabled={sending}>
              {sending ? "Sending..." : "Send code to email"}
            </button>

            {msg && (
              <p className={`notice ${success ? "notice--success" : "notice--error"}`} aria-live="polite">
                {msg}
              </p>
            )}
          </form>
        )}

        {codeSent && (
          <div className="form">
            <div className="field">
              <label className="field__label" htmlFor="code">Verification code</label>
              <input
                id="code"
                className="field__input"
                type="text"
                placeholder="Enter the code from your email"
                value={code}
                onChange={(e) => setCode(e.target.value)}
                inputMode="numeric"
                autoComplete="one-time-code"
                required
              />
            </div>

            <div style={{ display: "flex", gap: 10 }}>
              <button className="btn btn--primary" onClick={handleVerifyCode} disabled={verifying}>
                {verifying ? "Verifying..." : "Verify Code"}
              </button>
              <button
                className="btn"
                type="button"
                onClick={(e) => handleSendCode(e)}
                disabled={sending}
                title="Send again"
              >
                {sending ? "Sending..." : "Resend"}
              </button>
            </div>

            {msg && (
              <p className={`notice ${success ? "notice--success" : "notice--error"}`} aria-live="polite">
                {msg}
              </p>
            )}
          </div>
        )}
      </section>
    </main>
  );
}

export default ForgotPassword;

