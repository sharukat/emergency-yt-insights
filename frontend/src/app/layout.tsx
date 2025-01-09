import "./globals.css";
import { Inter } from "next/font/google";
import { Providers } from "./providers";
import {
  SidebarProvider,
  SidebarTrigger,
  SidebarInset,
} from "@/components/ui/sidebar";
import { AppSidebar } from "@/components/app-sidebar";
import Footer from "@/components/footer";

const inter = Inter({ subsets: ["latin"] });

export const metadata = {
  title: "ADERSIM | AI Assistant",
  description: "LLM-based drink driving awareness tool",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="!scroll-smooth">
      <body className={inter.className}>
        <Providers>
          <SidebarProvider>
            <AppSidebar />
            <SidebarInset>
              <div className="flex min-h-screen flex-col">
                <div className="flex items-center p-4">
                  <SidebarTrigger />
                </div>
                <main className="flex-1">{children}</main>
                <Footer />
              </div>
            </SidebarInset>
          </SidebarProvider>
        </Providers>
      </body>
    </html>
  );
}
