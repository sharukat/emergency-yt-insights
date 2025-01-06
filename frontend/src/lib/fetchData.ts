import fs from 'fs';
import path from 'path';
import { Questions } from './typings';

export const fetchQuestions = async () => {
  const filePath = path.join(process.cwd(), 'src', 'app', 'lib', 'sample_questions.json');
  const res = fs.readFileSync(filePath, 'utf8');
  const data = JSON.parse(res);
  const question: Questions[] = data.all_questions;
  return question;
};