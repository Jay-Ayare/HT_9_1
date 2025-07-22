import { Note, ProcessedNote, Suggestion, ApiError } from '../types';

const API_BASE = import.meta.env.VITE_REACT_APP_API_URL || 'http://localhost:3001';
const USE_MOCK_DATA = false; // Set to true to use mock data during development

interface SubmitNotesResponse {
  processed_notes: ProcessedNote[];
  suggestions: Suggestion[];
}

class ApiService {
  async submitNotes(notes: string[]): Promise<SubmitNotesResponse> {
    if (USE_MOCK_DATA) {
      // Keep mock data for development
      await new Promise(resolve => setTimeout(resolve, 2000));
      
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
        suggestions: [{
          id: 'mock-sugg-1',
          type: 'connection',
          title: 'Mock Suggestion',
          description: 'This is a mock suggestion for development',
          confidence: 0.8,
          relatedNoteIds: [processed_notes[0]?.id || ''],
          category: 'mock',
        }],
      };
    }

    try {
      console.log('Submitting notes to backend:', notes);
      
      const response = await fetch(`${API_BASE}/api/notes`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ notes }),
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`HTTP ${response.status}: ${response.statusText} - ${errorText}`);
      }

      const result = await response.json();
      console.log('Backend response:', result);
      
      return result;
    } catch (error) {
      console.error('Error submitting notes:', error);
      throw this.handleError(error);
    }
  }

  async getSuggestions(): Promise<Suggestion[]> {
    if (USE_MOCK_DATA) {
      await new Promise(resolve => setTimeout(resolve, 1000));
      return [];
    }

    try {
      const response = await fetch(`${API_BASE}/api/suggestions`);
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error fetching suggestions:', error);
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
      const response = await fetch(`${API_BASE}/api/notes/${noteId}/reprocess`, {
        method: 'POST',
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error reprocessing note:', error);
      throw this.handleError(error);
    }
  }

  async healthCheck(): Promise<{ status: string; timestamp: string }> {
    try {
      const response = await fetch(`${API_BASE}/api/health`);
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Health check failed:', error);
      throw this.handleError(error);
    }
  }

  private handleError(error: any): ApiError {
    if (error.name === 'TypeError' && error.message.includes('fetch')) {
      return {
        message: 'Unable to connect to server. Please check if the backend is running on port 3001.',
        status: 0
      };
    }

    return {
      message: error.message || 'An unexpected error occurred',
      status: error.status || 500
    };
  }
}

export const apiService = new ApiService();