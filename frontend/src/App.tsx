import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { NoteInput } from './components/NoteInput';
import { NoteList } from './components/NoteList';
import { NoteDetail } from './components/NoteDetail';
import GraphRAGQuery from './components/GraphRAGQuery';
import { Note, Suggestion, ApiError } from './types';
import { apiService } from './utils/api';
import { mockNotes } from './utils/mockData';
import { AlertCircle, Filter, X } from 'lucide-react';

// Loading Wave Component
const LoadingWave = () => (
  <div className="flex items-center gap-1">
    {[...Array(3)].map((_, i) => (
      <motion.div
        key={i}
        className="w-2 h-2 bg-[#7f5af0] rounded-full"
        animate={{ y: [0, -10, 0] }}
        transition={{
          duration: 0.6,
          repeat: Infinity,
          delay: i * 0.2,
        }}
      />
    ))}
  </div>
);

function App() {
  const [notes, setNotes] = useState<Note[]>(mockNotes);
  const [suggestions, setSuggestions] = useState<Suggestion[]>([]);
  const [selectedNoteId, setSelectedNoteId] = useState<string | null>(null);
  const [isReprocessing, setIsReprocessing] = useState(false);
  const [isLoadingSuggestions, setIsLoadingSuggestions] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedFilter, setSelectedFilter] = useState('all');
  const [showInput, setShowInput] = useState(!mockNotes.length);
  const [activeTab, setActiveTab] = useState<'notes' | 'graphrag'>('notes');

  // Load suggestions on mount
  // This is removed as there is no backend endpoint to get all suggestions initially.

  // Auto-select first note when notes change
  useEffect(() => {
    if (notes.length > 0 && !selectedNoteId) {
      setSelectedNoteId(notes[0].id);
    }
  }, [notes, selectedNoteId]);

  const handleSubmitNotes = async (noteTexts: string[]) => {
    setIsLoadingSuggestions(true);
    setError(null);

    // Create new notes for the UI immediately
    const newNotes: Note[] = noteTexts.map((text, index) => ({
      id: Date.now().toString() + index,
      content: text,
      timestamp: new Date(),
      sentiments: [],
      resources_needed: [],
      resources_available: [],
      processed: true,
    }));

    setNotes(prev => [...newNotes, ...prev]);
    setSelectedNoteId(newNotes[0]?.id || null);
    setShowInput(false);

    try {
      const response = await apiService.submitNotes(noteTexts);
      
      // Update the notes state with the processed data from the backend
      setNotes(prev => {
        const newNotesMap = new Map(response.processed_notes.map(n => [n.content, n]));
        return prev.map(note => {
          const processed = newNotesMap.get(note.content);
          return processed ? { ...note, ...processed, id: note.id } : note;
        });
      });

      // Add new suggestions to the existing list
      setSuggestions(prev => [...response.suggestions, ...prev]);
    } catch (err) {
      const error = err as ApiError;
      setError(`Failed to process notes: ${error.message}`);
    } finally {
      setIsLoadingSuggestions(false);
    }
  };

  const handleReprocessNote = async (noteId: string) => {
    setIsReprocessing(true);
    setError(null);

    try {
      // This functionality requires a dedicated backend endpoint which does not exist yet.
      setError("Reprocessing is not yet implemented on the backend.");
    } catch (err) {
      const error = err as ApiError;
      setError(`Failed to reprocess note: ${error.message}`);
    } finally {
      setIsReprocessing(false);
    }
  };

  const selectedNote = notes.find(note => note.id === selectedNoteId);

  // Get unique filter options
  const filterOptions = ['all', 'positive', 'negative', 'anxious', 'hopeful', 'creative', 'overwhelmed'];

  return (
    <div className="min-h-screen bg-[#0f0f1a] text-[#e0e0ff]">
      {/* Header */}
      <motion.header 
        initial={{ y: -50, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.5 }}
        className="bg-[#1a1a2e] border-b border-[#444466] py-6 backdrop-blur-sm"
      >
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between">
            <div className="text-center flex-1">
              <motion.h1 
                initial={{ scale: 0.8, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                transition={{ delay: 0.2, duration: 0.5 }}
                className="text-4xl font-bold bg-gradient-to-r from-[#7f5af0] to-blue-400 bg-clip-text text-transparent"
              >
                HiddenThread
              </motion.h1>
              <motion.p 
                initial={{ y: 10, opacity: 0 }}
                animate={{ y: 0, opacity: 1 }}
                transition={{ delay: 0.4, duration: 0.5 }}
                className="text-[#e0e0ff]/70 mt-2"
              >
                Discover connections in your thoughts
              </motion.p>
            </div>
            <motion.div 
              initial={{ x: 50, opacity: 0 }}
              animate={{ x: 0, opacity: 1 }}
              transition={{ delay: 0.3, duration: 0.5 }}
              className="flex items-center gap-4"
            >
              {!showInput && notes.length > 0 && (
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={() => setShowInput(true)}
                  className="px-4 py-2 bg-[#7f5af0] hover:bg-[#7f5af0]/80 text-white rounded-lg transition-all duration-200 hover:shadow-lg hover:shadow-[#7f5af0]/30"
                >
                  Add Notes
                </motion.button>
              )}
              {notes.length > 0 && (
                <div className="flex items-center gap-2">
                  <Filter className="w-4 h-4 text-[#e0e0ff]/50" />
                  <motion.select
                    whileFocus={{ scale: 1.02 }}
                    value={selectedFilter}
                    onChange={(e) => setSelectedFilter(e.target.value)}
                    className="bg-[#1a1a2e] border border-[#444466] text-[#e0e0ff] rounded-lg px-3 py-2 focus:border-[#7f5af0] focus:outline-none transition-all duration-200 hover:border-[#7f5af0]/50"
                  >
                    {filterOptions.map(option => (
                      <option key={option} value={option}>
                        {option === 'all' ? 'All Notes' : option.charAt(0).toUpperCase() + option.slice(1)}
                      </option>
                    ))}
                  </motion.select>
                </div>
              )}
            </motion.div>
          </div>
        </div>
      </motion.header>

      {/* Error Banner */}
      <AnimatePresence>
        {error && (
          <motion.div 
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="bg-red-500/10 border border-red-500/20 mx-4 mt-4 p-4 rounded-lg flex items-center justify-between backdrop-blur-sm"
          >
            <div className="flex items-center gap-3">
              <motion.div
                animate={{ rotate: [0, 15, -15, 0] }}
                transition={{ duration: 0.5, repeat: 3 }}
              >
                <AlertCircle className="w-5 h-5 text-red-400" />
              </motion.div>
              <span className="text-red-400">{error}</span>
            </div>
            <motion.button
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.9 }}
              onClick={() => setError(null)}
              className="text-red-400 hover:text-red-300"
            >
              <X className="w-4 h-4" />
            </motion.button>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Loading Suggestions Banner */}
      <AnimatePresence>
        {isLoadingSuggestions && (
          <motion.div 
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="bg-blue-500/10 border border-blue-500/20 mx-4 mt-4 p-4 rounded-lg backdrop-blur-sm"
          >
            <div className="flex items-center gap-3">
              <LoadingWave />
              <span className="text-blue-400">Loading AI suggestions...</span>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      <motion.div 
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.5, duration: 0.5 }}
        className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8"
      >
        {showInput ? (
          <div className="max-w-2xl mx-auto">
            <NoteInput
              onSubmit={handleSubmitNotes}
              isLoading={isLoadingSuggestions}
            />
            {notes.length > 0 && (
              <div className="mt-6 text-center">
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={() => setShowInput(false)}
                  className="text-[#7f5af0] hover:text-[#7f5af0]/80 transition-colors"
                >
                  Back to Notes
                </motion.button>
              </div>
            )}
          </div>
        ) : (
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="space-y-6"
          >
            {/* Tab Navigation */}
            <div className="flex space-x-1 bg-[#1a1a2e] rounded-lg p-1 border border-[#444466]">
              <button
                onClick={() => setActiveTab('notes')}
                className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors ${
                  activeTab === 'notes'
                    ? 'bg-[#7f5af0] text-white'
                    : 'text-[#e0e0ff]/70 hover:text-[#e0e0ff]'
                }`}
              >
                Notes & Suggestions
              </button>
              <button
                onClick={() => setActiveTab('graphrag')}
                className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors ${
                  activeTab === 'graphrag'
                    ? 'bg-[#7f5af0] text-white'
                    : 'text-[#e0e0ff]/70 hover:text-[#e0e0ff]'
                }`}
              >
                GraphRAG Query
              </button>
            </div>

            {/* Tab Content */}
            {activeTab === 'notes' ? (
              <motion.div 
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5 }}
                className="grid grid-cols-1 lg:grid-cols-3 gap-8 h-[calc(100vh-300px)]"
              >
                {/* Left Panel - Notes List */}
                <motion.div 
                  initial={{ x: -50, opacity: 0 }}
                  animate={{ x: 0, opacity: 1 }}
                  transition={{ delay: 0.2, duration: 0.5 }}
                  className="lg:col-span-1 space-y-4"
                >
                  <div className="flex items-center justify-between">
                    <h2 className="text-xl font-semibold text-[#e0e0ff]">Your Notes</h2>
                    <motion.span 
                      key={notes.length}
                      initial={{ scale: 1.2 }}
                      animate={{ scale: 1 }}
                      className="text-sm text-[#e0e0ff]/50"
                    >
                      {notes.filter(n => selectedFilter === 'all' || 
                        [...(n.sentiments || []), ...(n.resources_needed || []), ...(n.resources_available || [])]
                          .some(cat => cat.toLowerCase().includes(selectedFilter.toLowerCase()))
                      ).length} notes
                    </motion.span>
                  </div>
                  <motion.div 
                    whileHover={{ boxShadow: '0 10px 25px -5px rgba(127, 90, 240, 0.1)' }}
                    className="bg-[#1a1a2e] rounded-lg border border-[#444466] p-4 h-full overflow-y-auto backdrop-blur-sm"
                  >
                    <NoteList
                      notes={notes}
                      selectedNoteId={selectedNoteId}
                      onSelectNote={setSelectedNoteId}
                      selectedFilter={selectedFilter}
                      isLoading={isLoadingSuggestions}
                    />
                  </motion.div>
                </motion.div>

                {/* Right Panel - Note Details */}
                <motion.div 
                  initial={{ x: 50, opacity: 0 }}
                  animate={{ x: 0, opacity: 1 }}
                  transition={{ delay: 0.4, duration: 0.5 }}
                  className="lg:col-span-2"
                >
                  {selectedNote ? (
                    <div className="h-full overflow-y-auto">
                      <NoteDetail
                        note={selectedNote}
                        suggestions={suggestions}
                        onReprocess={handleReprocessNote}
                        isReprocessing={isReprocessing}
                      />
                    </div>
                  ) : (
                    <motion.div 
                      initial={{ scale: 0.9, opacity: 0 }}
                      animate={{ scale: 1, opacity: 1 }}
                      className="bg-[#1a1a2e] rounded-lg border border-[#444466] h-full flex items-center justify-center backdrop-blur-sm"
                    >
                      <div className="text-center text-[#e0e0ff]/50">
                        <h3 className="text-lg font-medium mb-2">Select a note</h3>
                        <p>Choose a note from the list to view details and suggestions</p>
                      </div>
                    </motion.div>
                  )}
                </motion.div>
              </motion.div>
            ) : (
              <motion.div 
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5 }}
                className="h-[calc(100vh-300px)]"
              >
                <GraphRAGQuery notes={notes.map(n => n.content)} />
              </motion.div>
            )}
          </motion.div>
        )}
      </motion.div>
    </div>
  );
}

export default App;