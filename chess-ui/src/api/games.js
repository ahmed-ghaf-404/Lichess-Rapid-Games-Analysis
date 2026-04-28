import { apiGet } from "./client";

export function fetchGamesByUser(username) {
  return apiGet(`/games/user/${username}`);
}