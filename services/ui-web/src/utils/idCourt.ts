export function idCourt(id?: string | null, debut = 6, fin = 4): string {
  if (!id) return "";
  if (id.length <= debut + fin + 1) return id;
  return `${id.slice(0, debut)}…${id.slice(-fin)}`;
}
