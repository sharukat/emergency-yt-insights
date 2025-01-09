// app/page.tsx
import { Questions } from '@/lib/typings';
import ExtractPage from '@/pages/extraction_page'

export default async function Home() {
  
  return (
    <main className='flex flex-col items-center px-4'>
      <ExtractPage />
    </main>
  );
}