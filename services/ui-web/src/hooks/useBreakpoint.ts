import { useEffect, useState } from "react";

export function useBreakpoint(maxWidth: number = 768): boolean {
  const [isMobile, setIsMobile] = useState<boolean>(
    window.matchMedia ? window.matchMedia(`(max-width: ${maxWidth}px)`).matches : false
  );

  useEffect(() => {
    const mq = window.matchMedia(`(max-width: ${maxWidth}px)`);

    const handler = (event: MediaQueryListEvent) => {
      setIsMobile(event.matches);
    };

    mq.addEventListener("change", handler);
    return () => mq.removeEventListener("change", handler);
  }, [maxWidth]);

  return isMobile;
}
