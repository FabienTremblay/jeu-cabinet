// src/hooks/usePolling.ts
import { useEffect, useRef } from "react";

/**
 * Hook simple de polling :
 * - fn : fonction appelée à chaque intervalle (peut être async)
 * - delayMs : intervalle en ms
 * - enabled : si false, le polling est désactivé
 */
export function usePolling(
  fn: () => void | Promise<void>,
  delayMs: number,
  enabled: boolean
): void {
  const savedCallback = useRef<() => void | Promise<void>>();

  // mémorise la dernière version de fn
  useEffect(() => {
    savedCallback.current = fn;
  }, [fn]);

  useEffect(() => {
    if (!enabled) {
      return;
    }

    let isCancelled = false;

    async function tick() {
      if (!savedCallback.current || isCancelled) return;
      try {
        await savedCallback.current();
      } catch (err) {
        // on logge dans la console, mais on ne casse pas la boucle
        console.error("Erreur dans usePolling callback :", err);
      }
    }

    // premier appel immédiat
    tick();

    const id = setInterval(tick, delayMs);

    return () => {
      isCancelled = true;
      clearInterval(id);
    };
  }, [delayMs, enabled]);
}

