export interface Note {
  id: string;
  content: string;
  timestamp: Date;
  sentiments?: string[];
  resources_needed?: string[];
  resources_available?: string[];
  processed: boolean;
}

export interface Suggestion {
  id: string;
  noteId: string;
  need: string;
  availability: string;
  suggestion: string;
}

export interface ProcessedNote {
  id: string;
  content: string;
  sentiments: string[];
  resources_needed: string[];
  resources_available: string[];
}

export interface ApiError {
  message: string;
  status?: number;
}