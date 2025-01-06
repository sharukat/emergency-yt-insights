// app/page.tsx
import { Questions } from '@/lib/typings';
import ExtractPage from '@/pages/extraction_page'

export default async function Home() {
  
  return (
    <main>
      <ExtractPage />
    </main>
  );
}