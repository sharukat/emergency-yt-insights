import { promises as fs } from 'fs';
import path from 'path';
import { Collection } from "@/lib/typings"

// export const fetchQuestions = async () => {
//   const filePath = path.join(process.cwd(), 'src', 'app', 'lib', 'sample_questions.json');
//   const res = fs.readFileSync(filePath, 'utf8');
//   const data = JSON.parse(res);
//   const question: Questions[] = data.all_questions;
//   return question;
// };

export const fetchCollections = async () => {
  const res = await fetch("http://130.63.65.112:80/collections", {
    method: "POST",
    mode: "cors",
    headers: { "Content-Type": "application/json" }
  });
  const data = await res.json()
  const collections: Collection[] = data.response
  return collections
}

// export const fetchCollections = async () => {
//   const filePath = path.join(process.cwd(), 'src', 'lib', 'sample_collections.json');
//   const res = await fs.readFile(filePath, 'utf8');
//   const data = JSON.parse(res);
//   const collections: Collection[] = data.all_collections
//   return collections
// }