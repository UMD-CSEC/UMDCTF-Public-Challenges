import { createContext, useContext } from "react";
import { API_URL } from "./constants";

declare global {
  interface Window {
    username: string;
    sessionNumber: number;
  }
}

export async function ensureSessionNumber() {
  if (window.sessionNumber !== undefined) {
    return;
  }

  const response = await fetch(`${API_URL}/start-session`, {
    method: "POST",
    credentials: 'include'
  });
  if (!response.ok) {
    return;
  }

  const { sessionNumber } = await response.json();
  window.sessionNumber = sessionNumber;
}

export type AccountContextType = [boolean, (loggedIn: boolean) => void];
export const AccountContext = createContext<AccountContextType | undefined>(undefined);

export function useLoggedIn() {
  const ctx = useContext(AccountContext);
  if (!ctx) throw new Error("Missing AccountContext.Provider");
  return ctx;
}