import React, { useState } from 'react';
import { Note, Suggestion } from '../types';
import { SuggestionCard } from './SuggestionCard';
import { RefreshCw, Heart, PenTool as Tool, Package } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

interface NoteDetailProps {
  note: Note;
  suggestions: Suggestion[];
  onReprocess: (noteId: string) => void;
  isReprocessing: boolean;
}

export const NoteDetail: React.FC<NoteDetailProps> = ({
  note,
  suggestions,
  onReprocess,
  isReprocessing
}) => {
  const [expandedSections, setExpandedSections] = useState({
    sentiments: true,
    needs: true,
    available: true,
    suggestions: true
  });

  const toggleSection = (section: keyof typeof expandedSections) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }));
  };

  const formatDate = (date: Date | string) => {
    const dateObj = date instanceof Date ? date : new Date(date);
    return new Intl.DateTimeFormat('en-US', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    }).format(dateObj);
  };

  const noteSuggestions = suggestions.filter(s => s.noteId === note.id);
  
  // Debug logging
  console.log('NoteDetail Debug:', {
    noteId: note.id,
    totalSuggestions: suggestions.length,
    suggestions: suggestions,
    noteSuggestions: noteSuggestions
  });

  return (
    <motion.div 
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.5 }}
      className="space-y-6"
    >
      {/* Header */}
      <motion.div 
        initial={{ y: -20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ delay: 0.1 }}
        className="bg-[#1a1a2e] rounded-lg p-6 border border-[#444466] hover:shadow-lg hover:shadow-[#7f5af0]/10 transition-all duration-200"
      >
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-2xl font-bold text-[#e0e0ff]">Note Details</h2>
          {!note.processed && (
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => onReprocess(note.id)}
              disabled={isReprocessing}
              className="flex items-center gap-2 px-4 py-2 bg-[#7f5af0] hover:bg-[#7f5af0]/80 disabled:opacity-50 text-white rounded-lg transition-all duration-200 hover:shadow-lg hover:shadow-[#7f5af0]/30"
              title="Reprocess this note"
            >
              <motion.div
                animate={isReprocessing ? { rotate: 360 } : {}}
                transition={{ duration: 1, repeat: isReprocessing ? Infinity : 0, ease: "linear" }}
              >
                <RefreshCw className="w-4 h-4" />
              </motion.div>
              {isReprocessing ? 'Reprocessing...' : 'Reprocess Note'}
            </motion.button>
          )}
        </div>
        
        <p className="text-[#e0e0ff]/70 text-sm mb-4">{formatDate(note.timestamp)}</p>
        
        <motion.div 
          whileHover={{ scale: 1.01 }}
          className="bg-[#0f0f1a] p-4 rounded-lg border border-[#444466] backdrop-blur-sm"
        >
          <p className="text-[#e0e0ff] leading-relaxed">{note.content}</p>
        </motion.div>
      </motion.div>

      {note.processed ? (
        <>
          {/* Analysis Results */}
          <motion.div 
            initial={{ y: 20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ delay: 0.2 }}
            className="grid gap-4"
          >
            {/* Sentiments */}
            <motion.div 
              whileHover={{ scale: 1.01 }}
              className="bg-[#1a1a2e] rounded-lg border border-[#444466] overflow-hidden hover:shadow-lg hover:shadow-pink-500/10 transition-all duration-200"
            >
              <motion.button
                whileHover={{ backgroundColor: 'rgba(127, 90, 240, 0.05)' }}
                onClick={() => toggleSection('sentiments')}
                className="w-full flex items-center justify-between p-4 transition-colors"
              >
                <div className="flex items-center gap-3">
                  <motion.div
                    whileHover={{ scale: 1.2 }}
                    animate={{ scale: [1, 1.1, 1] }}
                    transition={{ duration: 2, repeat: Infinity }}
                  >
                    <Heart className="w-5 h-5 text-pink-400" />
                  </motion.div>
                  <span className="text-lg font-semibold text-[#e0e0ff]">Sentiments</span>
                  <span className="text-sm text-[#e0e0ff]/50">({note.sentiments?.length || 0})</span>
                </div>
                <motion.div 
                  animate={{ rotate: expandedSections.sentiments ? 180 : 0 }}
                  transition={{ duration: 0.2 }}
                >
                  ▼
                </motion.div>
              </motion.button>
              
              <AnimatePresence>
                {expandedSections.sentiments && (
                  <motion.div 
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: 'auto', opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    transition={{ duration: 0.3 }}
                    className="px-4 pb-4 overflow-hidden"
                  >
                    <div className="flex flex-wrap gap-2">
                      {note.sentiments?.map((sentiment, index) => (
                        <motion.span
                          key={index}
                          initial={{ scale: 0, opacity: 0 }}
                          animate={{ scale: 1, opacity: 1 }}
                          transition={{ delay: index * 0.1 }}
                          whileHover={{ scale: 1.05 }}
                          className="px-3 py-1 bg-pink-500/20 text-pink-300 rounded-full text-sm"
                        >
                          {sentiment}
                        </motion.span>
                      )) || <span className="text-[#e0e0ff]/50 text-sm">No sentiments detected</span>}
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </motion.div>

            {/* Resources Needed */}
            <motion.div 
              whileHover={{ scale: 1.01 }}
              className="bg-[#1a1a2e] rounded-lg border border-[#444466] overflow-hidden hover:shadow-lg hover:shadow-red-500/10 transition-all duration-200"
            >
              <motion.button
                whileHover={{ backgroundColor: 'rgba(127, 90, 240, 0.05)' }}
                onClick={() => toggleSection('needs')}
                className="w-full flex items-center justify-between p-4 transition-colors"
              >
                <div className="flex items-center gap-3">
                  <motion.div
                    whileHover={{ scale: 1.2, rotate: 15 }}
                  >
                    <Tool className="w-5 h-5 text-red-400" />
                  </motion.div>
                  <span className="text-lg font-semibold text-[#e0e0ff]">Resources Needed</span>
                  <span className="text-sm text-[#e0e0ff]/50">({note.resources_needed?.length || 0})</span>
                </div>
                <motion.div 
                  animate={{ rotate: expandedSections.needs ? 180 : 0 }}
                  transition={{ duration: 0.2 }}
                >
                  ▼
                </motion.div>
              </motion.button>
              
              <AnimatePresence>
                {expandedSections.needs && (
                  <motion.div 
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: 'auto', opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    transition={{ duration: 0.3 }}
                    className="px-4 pb-4 overflow-hidden"
                  >
                    <div className="flex flex-wrap gap-2">
                      {note.resources_needed?.map((resource, index) => (
                        <motion.span
                          key={index}
                          initial={{ scale: 0, opacity: 0 }}
                          animate={{ scale: 1, opacity: 1 }}
                          transition={{ delay: index * 0.1 }}
                          whileHover={{ scale: 1.05 }}
                          className="px-3 py-1 bg-red-500/20 text-red-300 rounded-full text-sm"
                        >
                          {resource}
                        </motion.span>
                      )) || <span className="text-[#e0e0ff]/50 text-sm">No resources needed identified</span>}
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </motion.div>

            {/* Resources Available */}
            <motion.div 
              whileHover={{ scale: 1.01 }}
              className="bg-[#1a1a2e] rounded-lg border border-[#444466] overflow-hidden hover:shadow-lg hover:shadow-green-500/10 transition-all duration-200"
            >
              <motion.button
                whileHover={{ backgroundColor: 'rgba(127, 90, 240, 0.05)' }}
                onClick={() => toggleSection('available')}
                className="w-full flex items-center justify-between p-4 transition-colors"
              >
                <div className="flex items-center gap-3">
                  <motion.div
                    whileHover={{ scale: 1.2 }}
                    animate={{ y: [0, -2, 0] }}
                    transition={{ duration: 2, repeat: Infinity }}
                  >
                    <Package className="w-5 h-5 text-green-400" />
                  </motion.div>
                  <span className="text-lg font-semibold text-[#e0e0ff]">Resources Available</span>
                  <span className="text-sm text-[#e0e0ff]/50">({note.resources_available?.length || 0})</span>
                </div>
                <motion.div 
                  animate={{ rotate: expandedSections.available ? 180 : 0 }}
                  transition={{ duration: 0.2 }}
                >
                  ▼
                </motion.div>
              </motion.button>
              
              <AnimatePresence>
                {expandedSections.available && (
                  <motion.div 
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: 'auto', opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    transition={{ duration: 0.3 }}
                    className="px-4 pb-4 overflow-hidden"
                  >
                    <div className="flex flex-wrap gap-2">
                      {note.resources_available?.map((resource, index) => (
                        <motion.span
                          key={index}
                          initial={{ scale: 0, opacity: 0 }}
                          animate={{ scale: 1, opacity: 1 }}
                          transition={{ delay: index * 0.1 }}
                          whileHover={{ scale: 1.05 }}
                          className="px-3 py-1 bg-green-500/20 text-green-300 rounded-full text-sm"
                        >
                          {resource}
                        </motion.span>
                      )) || <span className="text-[#e0e0ff]/50 text-sm">No available resources identified</span>}
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </motion.div>
          </motion.div>

          {/* Suggestions */}
          {noteSuggestions.length > 0 && (
            <motion.div 
              initial={{ y: 20, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ delay: 0.4 }}
              whileHover={{ scale: 1.01 }}
              className="bg-[#1a1a2e] rounded-lg border border-[#444466] overflow-hidden hover:shadow-lg hover:shadow-[#7f5af0]/10 transition-all duration-200"
            >
              <motion.button
                whileHover={{ backgroundColor: 'rgba(127, 90, 240, 0.05)' }}
                onClick={() => toggleSection('suggestions')}
                className="w-full flex items-center justify-between p-4 transition-colors"
              >
                <div className="flex items-center gap-3">
                  <motion.div 
                    className="w-5 h-5 bg-gradient-to-r from-[#7f5af0] to-blue-400 rounded-full"
                    whileHover={{ scale: 1.2 }}
                    animate={{ 
                      boxShadow: [
                        '0 0 0 0 rgba(127, 90, 240, 0.7)',
                        '0 0 0 10px rgba(127, 90, 240, 0)',
                        '0 0 0 0 rgba(127, 90, 240, 0)'
                      ]
                    }}
                    transition={{ duration: 2, repeat: Infinity }}
                  />
                  <span className="text-lg font-semibold text-[#e0e0ff]">AI Suggestions</span>
                  <span className="text-sm text-[#e0e0ff]/50">({noteSuggestions.length})</span>
                </div>
                <motion.div 
                  animate={{ rotate: expandedSections.suggestions ? 180 : 0 }}
                  transition={{ duration: 0.2 }}
                >
                  ▼
                </motion.div>
              </motion.button>
              
              <AnimatePresence>
                {expandedSections.suggestions && (
                  <motion.div 
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: 'auto', opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    transition={{ duration: 0.3 }}
                    className="p-4 space-y-4 overflow-hidden"
                  >
                    {noteSuggestions.map((suggestion, index) => (
                      <motion.div
                        key={suggestion.id}
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: index * 0.1 }}
                      >
                        <SuggestionCard suggestion={suggestion} />
                      </motion.div>
                    ))}
                  </motion.div>
                )}
              </AnimatePresence>
            </motion.div>
          )}
        </>
      ) : (
        <motion.div 
          initial={{ scale: 0.9, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ delay: 0.2 }}
          className="bg-[#1a1a2e] rounded-lg p-8 border border-[#444466] text-center backdrop-blur-sm"
        >
          <motion.div 
            animate={{ rotate: 360 }}
            transition={{ duration: 3, repeat: Infinity, ease: "linear" }}
            className="w-16 h-16 bg-yellow-500/20 rounded-full flex items-center justify-center mx-auto mb-4"
          >
            <RefreshCw className="w-8 h-8 text-yellow-400" />
          </motion.div>
          <h3 className="text-xl font-semibold text-[#e0e0ff] mb-2">Note Not Processed</h3>
          <p className="text-[#e0e0ff]/70 mb-4">This note hasn't been analyzed yet. Click the reprocess button to analyze it.</p>
        </motion.div>
      )}
    </motion.div>
  );
};