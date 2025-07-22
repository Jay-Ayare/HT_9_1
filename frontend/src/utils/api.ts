import { Note, ProcessedNote, Suggestion, ApiError } from '../types';
import { mockSuggestions } from './mockData';

const API_BASE = import.meta.env.VITE_REACT_APP_API_URL || 'http://localhost:3001';
const USE_MOCK_DATA = true; // Set to false when backend is available

interface SubmitNotesResponse {
  processed_notes: ProcessedNote[];
  suggestions: Suggestion[];
}

class ApiService {
  async submitNotes(notes: string[]): Promise<SubmitNotesResponse> {
    if (USE_MOCK_DATA) {
      // Simulate API delay
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      // Mock processing - your App.tsx expects this exact format
      const processed_notes: ProcessedNote[] = notes.map((content, index) => ({
        id: Date.now().toString() + index,
        content,
        timestamp: new Date(),
        sentiments: ['positive', 'motivated'],
        resources_needed: ['guidance', 'support'],
        resources_available: ['skills', 'knowledge'],
        processed: true,
      }));

      return {
        processed_notes,
        suggestions: mockSuggestions.slice(0, 2), // Return a few suggestions
      };
    }

    try {
      const response = await fetch(`${API_BASE}/notes`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ notes }),
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async getSuggestions(): Promise<Suggestion[]> {
    if (USE_MOCK_DATA) {
      // Simulate API delay
      await new Promise(resolve => setTimeout(resolve, 1000));
      return mockSuggestions;
    }

    try {
      const response = await fetch(`${API_BASE}/suggestions`);
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async reprocessNote(noteId: string): Promise<ProcessedNote> {
    if (USE_MOCK_DATA) {
      await new Promise(resolve => setTimeout(resolve, 1500));
      return {
        id: noteId,
        content: "Reprocessed note content",
        timestamp: new Date(),
        sentiments: ['hopeful', 'determined'],
        resources_needed: ['guidance'],
        resources_available: ['experience'],
        processed: true,
      };
    }

    try {
      const response = await fetch(`${API_BASE}/notes/${noteId}/reprocess`, {
        method: 'POST',
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      throw this.handleError(error);
    }
  }

  private handleError(error: any): ApiError {
    if (error.name === 'TypeError' && error.message.includes('fetch')) {
      return {
        message: 'Unable to connect to server. Please check your connection.',
        status: 0
      };
    }

    return {
      message: error.message || 'An unexpected error occurred',
      status: error.status
    };
  }
}

export const apiService = new ApiService();