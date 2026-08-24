import { Chess } from "chess.js";


export function getPositionKey(fen) {
  return String(fen || "").trim().split(/\s+/).slice(0, 4).join(" ");
}


export function getMovesForPosition(lines, fen) {
  const key = getPositionKey(fen);
  return lines.flatMap((line) =>
    (line.moves || [])
      .filter((move) => move.position_key === key)
      .map((move) => ({ ...move, lineId: line.id, lineName: line.name }))
  );
}


export function buildRepertoireTree(lines) {
  const childrenByParent = new Map();
  for (const line of lines) {
    const parentKey = line.parent_line_id || "root";
    const children = childrenByParent.get(parentKey) || [];
    children.push(line);
    childrenByParent.set(parentKey, children);
  }

  const attachChildren = (line) => ({
    ...line,
    children: (childrenByParent.get(line.id) || []).map(attachChildren),
  });

  return (childrenByParent.get("root") || []).map(attachChildren);
}


export function inferOpeningName(games, line = []) {
  const currentMoves = line.map((node) => node.san).filter(Boolean);
  const matches = new Map();

  for (const game of games) {
    if (!game?.opening?.name || !game?.moves) continue;
    const gameMoves = game.moves.split(/\s+/).filter(Boolean);
    const matchesPrefix = currentMoves.every((move, index) => gameMoves[index] === move);
    if (!matchesPrefix) continue;

    const score = matches.get(game.opening.name) || 0;
    matches.set(game.opening.name, score + 1);
  }

  return [...matches.entries()].sort((a, b) => b[1] - a[1])[0]?.[0] || "Custom Opening";
}


export function suggestRepertoireLineName(openingName, formatter = null) {
  const name = String(openingName || "Custom Opening");
  let family;
  if (/sicilian/i.test(name)) family = "Sicilian";
  else if (/london/i.test(name)) family = "London";
  else if (/italian/i.test(name)) family = "Italian";
  else if (/traxler/i.test(name)) family = "Traxler";
  else {
    family = name
      .split(":", 1)[0]
      .replace(/\b(Defense|Game|Opening|System)\b/gi, "")
      .replace(/\s+/g, " ")
      .trim() || "Custom";
  }

  if (formatter) return formatter(family);
  return `My ${family || "Custom"} Lines`;
}


export function analyzeRepertoireDivergence(games, lines, username) {
  const normalizedUser = String(username || "").toLowerCase();
  const approvedByPosition = new Map();

  for (const line of lines) {
    for (const move of line.moves || []) {
      const choices = approvedByPosition.get(move.position_key) || [];
      choices.push({ ...move, lineName: line.name });
      approvedByPosition.set(move.position_key, choices);
    }
  }

  const divergences = [];
  let gamesWithRepertoirePositions = 0;

  for (const game of games) {
    const whiteId = game?.players?.white?.user?.id?.toLowerCase();
    const blackId = game?.players?.black?.user?.id?.toLowerCase();
    const playerColor = whiteId === normalizedUser ? "w" : blackId === normalizedUser ? "b" : null;
    if (!playerColor || !game?.moves) continue;

    const board = new Chess();
    let encounteredRepertoire = false;

    for (const san of game.moves.split(/\s+/).filter(Boolean)) {
      const beforeKey = getPositionKey(board.fen());
      const approved = approvedByPosition.get(beforeKey) || [];
      const isPlayerTurn = board.turn() === playerColor;
      const move = board.move(san);
      if (!move) break;

      if (isPlayerTurn && approved.length) {
        encounteredRepertoire = true;
        const playedUci = `${move.from}${move.to}${move.promotion || ""}`;
        if (!approved.some((choice) => choice.move_uci === playedUci)) {
          divergences.push({
            gameId: game.id,
            openingName: game.opening?.name || "Unknown opening",
            ply: board.history().length,
            playedSan: move.san,
            approvedMoves: approved.map((choice) => choice.move_san),
            lineNames: [...new Set(approved.map((choice) => choice.lineName))],
          });
          break;
        }
      }
    }

    if (encounteredRepertoire) gamesWithRepertoirePositions += 1;
  }

  return {
    gamesWithRepertoirePositions,
    divergenceCount: divergences.length,
    alignedCount: Math.max(0, gamesWithRepertoirePositions - divergences.length),
    divergences,
  };
}
