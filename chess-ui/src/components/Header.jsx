export default function Header({ username, gameCount }) {
  return (
    <header className="page-header">
      <h1>Chess Coach Explorer</h1>
      <p>
        Exploring {gameCount} games for <strong>{username}</strong>
      </p>
    </header>
  );
}