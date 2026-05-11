// src/api/apiClient.ts

import type { ApiErreur, ApiErreurType } from "../types/common";

/**
 * Normalise une base URL à partir d'une variable d'env Vite.
 * - baseUrlEnvVar : nom de la variable d'env (ex: "VITE_LOBBY_BASE_URL")
 * - defaultBaseUrl : valeur par défaut si la variable n'est pas définie
 */
function resolveBaseUrl(baseUrlEnvVar: string, defaultBaseUrl: string): string {
  // import.meta.env["VITE_..."] est la bonne façon en Vite
  const envValue = import.meta.env[baseUrlEnvVar] as string | undefined;
  const baseUrl = (envValue ?? defaultBaseUrl).replace(/\/$/, "");
  return baseUrl;
}

function lireJetonSession(): string | null {
  if (typeof window === "undefined") return null;
  try {
    const raw = window.sessionStorage.getItem("cabinet.session.joueur");
    if (!raw) return null;
    const data = JSON.parse(raw) as { jeton_session?: string };
    return data.jeton_session ?? null;
  } catch {
    return null;
  }
}

function construireHeadersJson(accepteContenu: boolean): HeadersInit {
  const headers: Record<string, string> = {
    Accept: "application/json",
  };
  if (accepteContenu) {
    headers["Content-Type"] = "application/json";
  }
  const jetonSession = lireJetonSession();
  if (jetonSession) {
    headers.Authorization = `Bearer ${jetonSession}`;
  }
  return headers;
}

/**
 * GET JSON générique.
 * Usage : const getLobbyJson = makeGetJson("VITE_LOBBY_BASE_URL", "http://lobby.cabinet.localhost");
 * puis : const data = await getLobbyJson("/api/.../truc");
 */
export function makeGetJson(baseUrlEnvVar: string, defaultBaseUrl: string) {
  const baseUrl = resolveBaseUrl(baseUrlEnvVar, defaultBaseUrl);

  return async function getJson<T>(path: string): Promise<T> {
    const cleanedPath = path.startsWith("/") ? path.slice(1) : path;
    const url = `${baseUrl}/${cleanedPath}`;

    const response = await fetch(url, {
      method: "GET",
      headers: construireHeadersJson(false),
    });

    return handleResponse<T>(response);
  };
}

/**
 * POST JSON générique.
 * Usage : const postLobbyJson = makePostJson("VITE_LOBBY_BASE_URL", "http://lobby.cabinet.localhost");
 * puis : const data = await postLobbyJson("/api/.../action", payload);
 */
export function makePostJson(baseUrlEnvVar: string, defaultBaseUrl: string) {
  const baseUrl = resolveBaseUrl(baseUrlEnvVar, defaultBaseUrl);

  return async function postJson<T, Body = unknown>(
    path: string,
    body: Body
  ): Promise<T> {
    const cleanedPath = path.startsWith("/") ? path.slice(1) : path;
    const url = `${baseUrl}/${cleanedPath}`;

    const response = await fetch(url, {
      method: "POST",
      headers: construireHeadersJson(true),
      body: JSON.stringify(body),
    });

    return handleResponse<T>(response);
  };
}

export function makePatchJson(baseUrlEnvVar: string, defaultBaseUrl: string) {
  const baseUrl = resolveBaseUrl(baseUrlEnvVar, defaultBaseUrl);

  return async function patchJson<T, Body = unknown>(
    path: string,
    body: Body
  ): Promise<T> {
    const cleanedPath = path.startsWith("/") ? path.slice(1) : path;
    const url = `${baseUrl}/${cleanedPath}`;

    const response = await fetch(url, {
      method: "PATCH",
      headers: construireHeadersJson(true),
      body: JSON.stringify(body),
    });

    return handleResponse<T>(response);
  };
}

/**
 * Gestion des réponses d'API : lève une ApiErreur typée en cas d'erreur HTTP.
 */
export async function handleResponse<T>(response: Response): Promise<T> {
  if (response.ok) {
    // 2xx
    return (await response.json()) as T;
  }

  let type: ApiErreurType = "inconnu";
  let message = `Erreur HTTP ${response.status}`;

  try {
    const data = (await response.json()) as any;
    if (typeof data?.detail === "string") {
      message = data.detail;
    }
  } catch {
    // réponse pas en JSON : on garde le message par défaut
  }

  if (response.status >= 500) {
    type = "serveur";
  } else if (response.status === 404) {
    type = "non_trouve";
  } else if (response.status === 401 || response.status === 403) {
    type = "auth";
  } else if (response.status >= 400) {
    type = "client";
  }

  const err: ApiErreur = { type, status: response.status, message };
  if (
    type === "auth" &&
    typeof window !== "undefined" &&
    message.startsWith("session_")
  ) {
    window.dispatchEvent(new CustomEvent("cabinet:session-expiree"));
  }
  throw err;
}

// Types utilitaires
export type ApiClientGet = ReturnType<typeof makeGetJson>;
export type ApiClientPost = ReturnType<typeof makePostJson>;
export type ApiClientPatch = ReturnType<typeof makePatchJson>;
export type { ApiErreur, ApiErreurType };
