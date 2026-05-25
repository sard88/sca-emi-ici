export function confirmCatalogAction(message: string) {
  if (typeof window === "undefined") return false;
  return window.confirm(message);
}
