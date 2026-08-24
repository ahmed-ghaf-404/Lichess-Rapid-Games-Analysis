export default function ErrorState({
  title = "Something went wrong",
  message,
  detail = "",
}) {
  return (
    <section className="state-message state-card" role="alert">
      <span className="state-icon" aria-hidden="true">!</span>
      <div>
        <h2>{title}</h2>
        <p className="error">{message}</p>
        {detail ? <p className="state-detail">{detail}</p> : null}
      </div>
    </section>
  );
}
