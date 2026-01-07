import React, { createContext, useContext, useState, useMemo } from "react";

export type VueMode = "auto" | "large" | "mobile";

interface DisplayContextValue {
  vueMode: VueMode;
  setVueMode: (mode: VueMode) => void;
}

const DisplayContext = createContext<DisplayContextValue | undefined>(
  undefined
);

export const DisplayProvider: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => {
  const [vueMode, setVueMode] = useState<VueMode>("auto");

  const value = useMemo(
    () => ({ vueMode, setVueMode }),
    [vueMode]
  );

  return (
    <DisplayContext.Provider value={value}>
      {children}
    </DisplayContext.Provider>
  );
};

export function useDisplay(): DisplayContextValue {
  const ctx = useContext(DisplayContext);
  if (!ctx) {
    throw new Error("useDisplay must be used within a DisplayProvider");
  }
  return ctx;
}
