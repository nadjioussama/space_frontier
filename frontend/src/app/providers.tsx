"use client";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ReactNode, useState } from "react";
import { OfflineBanner } from "@/components/OfflineBanner";

const HOUR = 60 * 60 * 1000;
const DAY = 24 * HOUR;

export function Providers({ children }: { children: ReactNode }) {
  const [client] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            // PLAN §6.2 L1 staleTime per-endpoint. Defaults here are conservative;
            // per-hook overrides in queries.ts tighten where needed.
            staleTime: HOUR,
            gcTime: DAY,
            retry: 1,
            refetchOnWindowFocus: false,
          },
        },
      })
  );
  return (
    <QueryClientProvider client={client}>
      <OfflineBanner />
      {children}
    </QueryClientProvider>
  );
}
