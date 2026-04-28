from app.services.repertoire_service import RepertoireService


class FeatureBuilder:
    def __init__(self):
        self.repertoire = RepertoireService()

    async def enrich(self, user_id: str, fen: str, candidates: list[dict]) -> list[dict]:
        enriched = []

        for candidate in candidates:
            repertoire_fit = await self.repertoire.get_move_fit(
                user_id=user_id,
                fen=fen,
                move_uci=candidate["move_uci"],
            )

            enriched.append(
                {
                    **candidate,
                    "repertoire_fit": repertoire_fit,
                }
            )

        return enriched