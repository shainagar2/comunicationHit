// src/api/password.js
import axios from "axios";

/**
 * Axios instance כללי לאפליקציה (אפשר לשים בקובץ נפרד אם תרצי).
 * אם השרת עובד עם קוקיז/Session (HttpOnly) יש לשמור withCredentials: true.
 * אם זה אותו דומיין/פורט, זה עדיין בטוח להשאיר true.
 */
const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || "", // למשל: http://localhost:4000
  withCredentials: true,
  headers: { "Content-Type": "application/json" },
});

// מייצרות הודעת שגיאה קריאה יותר
api.interceptors.response.use(
  (res) => res,
  (err) => {
    const msg =
      err?.response?.data?.message ||
      `${err?.response?.status || ""} ${err?.response?.statusText || "Request failed"}`.trim() ||
      "Request failed";
    return Promise.reject(new Error(msg));
  }
);

/**
 * שינוי סיסמה למשתמש המחובר (Server-side session / cookie)
 * השרת אמור לאמת שהבקשה מגיעה ממשתמש תקף (למשל Session / CSRF).
 * @param {string} newPassword - הסיסמה החדשה
 * @returns {Promise<any>} - מחזיר את data מהשרת (אם יש)
 */
export async function changePassword(newPassword) {
  const { data } = await api.post("/api/resetpassword", { newPassword });
  return data;
}

/*  📝 אם בעתיד תצטרכי גם גרסה עם טוקן/אימייל (למשל ל-flow של Forgot Password),
    אפשר לפתוח פונקציה נוספת:

export async function changePasswordWithToken({ email, token, newPassword }) {
  const { data } = await api.post("/auth/reset-password", { email, token, newPassword });
  return data;
}
*/
