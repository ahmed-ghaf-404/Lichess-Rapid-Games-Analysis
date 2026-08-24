import { useEffect, useRef, useState } from "react";

import { fetchContactChallenge, sendContactMessage } from "../api/contact";
import SiteFooter from "../components/SiteFooter";
import SiteNavigation from "../components/SiteNavigation";
import { useLocalization } from "../i18n/useLocalization";


const createEmptyForm = (subject) => ({
  name: "",
  email: "",
  subject,
  message: "",
  website: "",
});


export default function ContactPage() {
  const { t } = useLocalization();
  const defaultSubject = t("contact.defaultSubject");
  const previousDefaultSubject = useRef(defaultSubject);
  const [form, setForm] = useState(() => createEmptyForm(defaultSubject));
  const [challenge, setChallenge] = useState("");
  const [statusMessage, setStatusMessage] = useState("");
  const [error, setError] = useState("");
  const [sending, setSending] = useState(false);

  async function refreshChallenge() {
    try {
      const result = await fetchContactChallenge();
      setChallenge(result.challenge);
      setError("");
    } catch (challengeError) {
      setError(challengeError.message);
    }
  }

  useEffect(() => {
    refreshChallenge();
  }, []);

  useEffect(() => {
    setForm((current) => ({
      ...current,
      subject: current.subject === previousDefaultSubject.current
        ? defaultSubject
        : current.subject,
    }));
    previousDefaultSubject.current = defaultSubject;
  }, [defaultSubject]);

  function updateField(event) {
    setForm((current) => ({ ...current, [event.target.name]: event.target.value }));
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setSending(true);
    setError("");
    setStatusMessage("");

    try {
      const result = await sendContactMessage({ ...form, challenge });
      setStatusMessage(result.message || t("contact.sent"));
      setForm(createEmptyForm(defaultSubject));
      await refreshChallenge();
    } catch (submitError) {
      setError(submitError.message);
      await refreshChallenge();
    } finally {
      setSending(false);
    }
  }

  return (
    <main className="app-shell content-page-shell">
      <SiteNavigation activePath="/contact" />

      <article className="content-page contact-page">
        <header className="content-page-header">
          <span className="eyebrow">{t("contact.eyebrow")}</span>
          <h1>{t("contact.title")}</h1>
          <p>{t("contact.intro")}</p>
        </header>

        <form className="contact-form" onSubmit={handleSubmit}>
          <label>
            {t("contact.name")}
            <input name="name" value={form.name} onChange={updateField} minLength="2" maxLength="100" required />
          </label>
          <label>
            {t("contact.email")}
            <input name="email" type="email" value={form.email} onChange={updateField} maxLength="254" required />
          </label>
          <label className="contact-form-wide">
            {t("contact.subject")}
            <input name="subject" value={form.subject} onChange={updateField} minLength="3" maxLength="150" required />
          </label>
          <label className="contact-form-wide">
            {t("contact.message")}
            <textarea name="message" value={form.message} onChange={updateField} minLength="20" maxLength="4000" rows="8" required />
          </label>

          <label className="bot-trap" aria-hidden="true">
            {t("contact.website")}
            <input name="website" value={form.website} onChange={updateField} tabIndex="-1" autoComplete="off" />
          </label>

          <div className="contact-form-actions contact-form-wide">
            <button type="submit" disabled={sending || !challenge}>
              {sending ? t("contact.sending") : t("contact.send")}
            </button>
            <span className="form-privacy-note">
              {t("contact.protection")}
            </span>
          </div>

          {statusMessage ? <p className="form-success contact-form-wide" role="status">{statusMessage}</p> : null}
          {error ? <p className="error contact-form-wide" role="alert">{error}</p> : null}
        </form>
      </article>

      <SiteFooter />
    </main>
  );
}
