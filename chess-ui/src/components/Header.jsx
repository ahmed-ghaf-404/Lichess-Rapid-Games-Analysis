export default function Header({ username, gameCount, warmup }) {
  const startupCount = warmup?.startup?.completed ?? warmup?.completed ?? 0;
  const backgroundCount = warmup?.background?.completed ?? 0;

  return (
    <header className="page-header">
      <h1>Chess Coach Explorer</h1>
      <p>
        Exploring {gameCount} games for <strong>{username}</strong>
      </p>
      {warmup?.done ? (
        <p className="cache-status">
          Analysis buffer ready
          {startupCount ? ` · ${startupCount} startup positions warmed` : ""}
          {backgroundCount ? ` · ${backgroundCount} background positions warmed` : ""}
          {warmup.error ? ` · Warmup warning: ${warmup.error}` : ""}
        </p>
      ) : null}
    </header>
  );
}
