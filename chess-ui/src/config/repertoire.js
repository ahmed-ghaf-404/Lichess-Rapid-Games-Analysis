const configuredUsers = String(
  import.meta.env.VITE_REPERTOIRE_USERS || "ericrosen,chocoroku"
);

export const REPERTOIRE_USERS = configuredUsers
  .split(",")
  .map((user) => user.trim().toLowerCase())
  .filter(Boolean);


export function isRepertoireUser(username) {
  return REPERTOIRE_USERS.includes(String(username || "").trim().toLowerCase());
}
