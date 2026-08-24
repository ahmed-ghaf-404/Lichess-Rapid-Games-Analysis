import { useCallback, useEffect, useMemo, useState } from "react";

import {
  approveRepertoireMove,
  createRepertoireLine,
  fetchRepertoire,
  removeRepertoireLine,
  removeRepertoireMove,
} from "../api/repertoire";
import { isRepertoireUser } from "../config/repertoire";
import { getMovesForPosition } from "../utils/repertoire";


export function useRepertoire(username, fen) {
  const enabled = isRepertoireUser(username);
  const [lines, setLines] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const refresh = useCallback(async () => {
    if (!enabled) {
      setLines([]);
      setError("");
      return [];
    }

    setLoading(true);
    try {
      const result = await fetchRepertoire(username.toLowerCase());
      setLines(result);
      setError("");
      return result;
    } catch (requestError) {
      setError(requestError.message);
      return [];
    } finally {
      setLoading(false);
    }
  }, [enabled, username]);

  useEffect(() => {
    refresh();
  }, [refresh]);

  const currentMoves = useMemo(
    () => getMovesForPosition(lines, fen),
    [lines, fen]
  );

  const createLine = useCallback(async (line, writeKey) => {
    const created = await createRepertoireLine(
      { ...line, user_id: username.toLowerCase() },
      writeKey
    );
    await refresh();
    return created;
  }, [refresh, username]);

  const approveMove = useCallback(async (lineId, move, writeKey) => {
    const approved = await approveRepertoireMove(
      lineId,
      {
        user_id: username.toLowerCase(),
        fen_before: fen,
        move_uci: move.move_uci,
        move_san: move.move_san,
        source: "recommendation",
      },
      writeKey
    );
    await refresh();
    return approved;
  }, [fen, refresh, username]);

  const deleteMove = useCallback(async (lineId, moveId, writeKey) => {
    await removeRepertoireMove(lineId, moveId, username, writeKey);
    await refresh();
  }, [refresh, username]);

  const deleteLine = useCallback(async (lineId, writeKey) => {
    await removeRepertoireLine(lineId, username, writeKey);
    await refresh();
  }, [refresh, username]);

  return useMemo(
    () => ({
      enabled,
      lines,
      currentMoves,
      loading,
      error,
      refresh,
      createLine,
      approveMove,
      deleteMove,
      deleteLine,
    }),
    [
      enabled,
      lines,
      currentMoves,
      loading,
      error,
      refresh,
      createLine,
      approveMove,
      deleteMove,
      deleteLine,
    ]
  );
}
