export default function LoadingState({ message = "Loading...", detail = "", children = null }) {
  return (
    <section className="state-message state-card" aria-live="polite" aria-busy="true">
      <span className="loading-mark" aria-hidden="true" />
      <div>
        <h2>{message}</h2>
        {detail ? <p className="state-detail">{detail}</p> : null}
      </div>
      {children}
    </section>
  );
}
