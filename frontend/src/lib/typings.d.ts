export interface GeneratedResponse {
  response: string[];
}

export interface SelectedQuestion {
  categoryIndex: number | null;
  questionIndex: number | null;
}

export interface Questions {
  category: string;
  questions: string[];
}

export interface Videos {
  title: string;
  url: string;
  video_id: string;
}

export interface Collection {
  _type: "collections";
  key: string;
  label: string;
}

export type Status =
  | "Extracting..."
  | "Preprocessing..."
  | "Classifying..."
  | "Saving..."
  | "Chunking..."
  | "Completed"
  | "Error";
