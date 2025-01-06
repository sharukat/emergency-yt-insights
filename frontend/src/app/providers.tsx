// app/providers.tsx
"use client";

import { useEffect, useState } from "react";
import {NextUIProvider} from '@nextui-org/react'
import {ThemeProvider } from "next-themes";

export function Providers({children}: { children: React.ReactNode }) {
  const [isClient, setIsClient] = useState(false);

  useEffect(() => {
    setIsClient(true);
  }, []);

  return ( isClient ?
    <NextUIProvider>
      <ThemeProvider attribute="class" defaultTheme="system" enableSystem={true}>
        {children}
      </ThemeProvider>
    </NextUIProvider> : <></>
  )
}