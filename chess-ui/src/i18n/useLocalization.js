import { createContext, useContext } from "react";


export const LocalizationContext = createContext(null);

export function useLocalization() {
  const context = useContext(LocalizationContext);
  if (!context) throw new Error("useLocalization must be used within LocalizationProvider");
  return context;
}
