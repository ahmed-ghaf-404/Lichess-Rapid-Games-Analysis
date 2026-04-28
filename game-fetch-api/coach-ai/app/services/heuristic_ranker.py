class HeuristicRanker:
    @staticmethod
    def normalize_engine(cp: int | None, loss_cp: int | None) -> float:
        if cp is None:
            return 0.0

        # cp is from side-to-move perspective
        base = max(min((cp + 200) / 400, 1.0), 0.0)
        penalty = min((loss_cp or 0) / 200, 1.0)
        return max(base - 0.5 * penalty, 0.0)

    @staticmethod
    def sample_confidence(peer_games: int) -> float:
        # Smooth confidence curve:
        # 1 game -> tiny confidence
        # 20 games -> 0.5
        # 100 games -> strong confidence
        return peer_games / (peer_games + 20)

    @staticmethod
    def bayesian_win_rate(peer_win_rate: float, peer_games: int, prior: float = 0.5, prior_weight: int = 10) -> float:
        # Smooth noisy win rates toward 50%
        wins_equivalent = peer_win_rate * peer_games
        return (wins_equivalent + prior * prior_weight) / (peer_games + prior_weight)

    def score(self, candidate: dict) -> tuple[float, list[str]]:
        peer_frequency = candidate.get("peer_frequency", 0.0)
        peer_win_rate = candidate.get("peer_win_rate", 0.0)
        peer_games = candidate.get("peer_games", 0)

        engine_quality = self.normalize_engine(
            candidate.get("engine_eval_cp"),
            candidate.get("engine_loss_cp"),
        )
        repertoire_fit = candidate.get("repertoire_fit", 0.0)

        confidence = self.sample_confidence(peer_games)
        smoothed_win_rate = self.bayesian_win_rate(peer_win_rate, peer_games)

        adjusted_peer_frequency = peer_frequency * confidence
        adjusted_peer_win_rate = smoothed_win_rate * confidence

        score = (
            0.35 * adjusted_peer_win_rate
            + 0.25 * adjusted_peer_frequency
            + 0.25 * engine_quality
            + 0.15 * repertoire_fit
        )

        reasons = []

        if peer_games >= 50:
            reasons.append("large peer sample")
        elif peer_games >= 15:
            reasons.append("reasonable peer sample")
        elif peer_games > 0:
            reasons.append("small peer sample")

        if peer_frequency >= 0.25 and peer_games >= 10:
            reasons.append("common at your rating")
        elif peer_frequency >= 0.10 and peer_games >= 10:
            reasons.append("played often in this pool")

        if smoothed_win_rate >= 0.55 and peer_games >= 10:
            reasons.append("strong peer win rate")
        elif smoothed_win_rate >= 0.50 and peer_games >= 10:
            reasons.append("solid practical results")

        if candidate.get("engine_rank") == 1:
            reasons.append("top engine move")
        elif candidate.get("engine_rank") in {2, 3}:
            reasons.append("engine-approved")

        if repertoire_fit >= 0.5:
            reasons.append("fits your repertoire")
        elif repertoire_fit >= 0.2:
            reasons.append("close to your repertoire")

        return round(score, 4), reasons

    def rank(self, candidates: list[dict]) -> list[dict]:
        ranked = []
        for candidate in candidates:
            score, reasons = self.score(candidate)
            ranked.append(
                {
                    **candidate,
                    "score": score,
                    "reasons": reasons,
                }
            )

        ranked.sort(
            key=lambda x: (
                x["score"],
                x.get("peer_games", 0),
                x.get("peer_frequency", 0.0),
            ),
            reverse=True,
        )
        return ranked