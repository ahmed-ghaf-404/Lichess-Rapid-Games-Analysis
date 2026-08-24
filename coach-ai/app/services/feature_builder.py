from app.services.repertoire_service import RepertoireService


class FeatureBuilder:
    def __init__(self):
        self.repertoire = RepertoireService()

    async def enrich(self, user_id: str, fen: str, candidates: list[dict]) -> list[dict]:
        move_fits = await self.repertoire.get_move_fits(
            user_id=user_id,
            fen=fen,
            move_ucis=[candidate["move_uci"] for candidate in candidates],
        )
        return [
            {
                **candidate,
                "repertoire_fit": move_fits.get(candidate["move_uci"], 0.0),
            }
            for candidate in candidates
        ]
