export default function LoadingState({ message = "Loading...", detail = "", children = null }) {
  return (
    <div className="state-message">
      <div>{message}</div>
      {detail ? <p className="state-detail">{detail}</p> : null}
      {children}
    </div>
  );
}
