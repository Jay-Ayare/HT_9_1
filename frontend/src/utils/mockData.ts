import { Note, Suggestion } from '../types';

export const mockNotes: Note[] = [
  {
    id: '1',
    content: 'I feel really excited about starting this new project. There are so many possibilities and I can\'t wait to dive in.',
    timestamp: new Date('2024-01-15T10:30:00'),
    sentiments: ['positive', 'excited', 'motivated'],
    resources_needed: ['guidance', 'planning tools'],
    resources_available: ['enthusiasm', 'creativity', 'time'],
    processed: true,
  },
  {
    id: '2',
    content: 'Sometimes I worry that I\'m not making the right decisions. The uncertainty makes me anxious.',
    timestamp: new Date('2024-01-14T14:20:00'),
    sentiments: ['anxious', 'uncertain', 'worried'],
    resources_needed: ['support', 'clarity', 'confidence'],
    resources_available: ['self-awareness', 'willingness to learn'],
    processed: true,
  },
];

export const mockSuggestions: Suggestion[] = [
  {
    id: 'sugg-1',
    type: 'connection',
    title: 'Pattern: Excitement vs Overwhelm',
    description: 'Your notes show a pattern between high excitement for new projects and feeling overwhelmed by responsibilities.',
    confidence: 0.85,
    relatedNoteIds: ['1', '2'],
    category: 'emotional_balance',
  },
];