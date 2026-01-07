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
      headers: {
        Accept: "application/json",
      },
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

  return async function postJson<T>(path: string, body: unknown): Promise<T> {
    const cleanedPath = path.startsWith("/") ? path.slice(1) : path;
    const url = `${baseUrl}/${cleanedPath}`;

    const response = await fetch(url, {
      method: "POST",
      headers: {
        Accept: "application/json",
        "Content-Type": "application/json",
      },
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
  throw err;
}

// Types utilitaires
export type ApiClientGet = ReturnType<typeof makeGetJson>;
export type ApiClientPost = ReturnType<typeof makePostJson>;
export type { ApiErreur, ApiErreurType };

