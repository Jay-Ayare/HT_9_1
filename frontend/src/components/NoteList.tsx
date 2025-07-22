import React from 'react';
import { Note } from '../types';
import { Clock, AlertCircle, CheckCircle } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import Skeleton from 'react-loading-skeleton';
import 'react-loading-skeleton/dist/skeleton.css';

interface NoteListProps {
  notes: Note[];
  selectedNoteId: string | null;
  onSelectNote: (noteId: string) => void;
  selectedFilter: string;
  isLoading?: boolean;
}

export const NoteList: React.FC<NoteListProps> = ({ 
  notes, 
  selectedNoteId, 
  onSelectNote,
  selectedFilter,
  isLoading = false
}) => {
  const filteredNotes = notes.filter(note => {
    if (selectedFilter === 'all') return true;
    
    const allCategories = [
      ...(note.sentiments || []),
      ...(note.resources_needed || []),
      ...(note.resources_available || [])
    ];
    
    return allCategories.some(category => 
      category.toLowerCase().includes(selectedFilter.toLowerCase())
    );
  });

  const formatDate = (date: Date | string) => {
    const dateObj = date instanceof Date ? date : new Date(date);
    return new Intl.DateTimeFormat('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    }).format(dateObj);
  };

  const truncateText = (text: string, maxLength: number = 100) => {
    return text.length > maxLength ? text.substring(0, maxLength) + '...' : text;
  };

  if (isLoading) {
    return (
      <div className="space-y-3">
        {[...Array(3)].map((_, index) => (
          <div key={index} className="p-4 rounded-lg bg-[#1a1a2e] border border-[#444466]">
            <div className="flex items-start justify-between mb-2">
              <Skeleton height={16} width={80} baseColor="#1a1a2e" highlightColor="#444466" />
              <Skeleton height={16} width={60} baseColor="#1a1a2e" highlightColor="#444466" />
            </div>
            <Skeleton count={3} height={16} baseColor="#1a1a2e" highlightColor="#444466" className="mb-3" />
            <div className="flex gap-2">
              <Skeleton height={24} width={60} baseColor="#1a1a2e" highlightColor="#444466" />
              <Skeleton height={24} width={80} baseColor="#1a1a2e" highlightColor="#444466" />
            </div>
          </div>
        ))}
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {filteredNotes.length === 0 ? (
        <motion.div 
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="text-center py-8 text-[#e0e0ff]/50"
        >
          {selectedFilter === 'all' ? 'No notes yet. Add your first note to get started!' : 'No notes match the current filter.'}
        </motion.div>
      ) : (
        <AnimatePresence>
          {filteredNotes.map((note, index) => (
            <motion.div
              key={note.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3, delay: index * 0.1 }}
              whileHover={{ scale: 1.02, y: -2 }}
              onClick={() => onSelectNote(note.id)}
              className={`p-4 rounded-lg border transition-all duration-200 cursor-pointer ${
                selectedNoteId === note.id
                  ? 'bg-[#7f5af0]/10 border-[#7f5af0] shadow-lg shadow-[#7f5af0]/20'
                  : 'bg-[#1a1a2e] border-[#444466] hover:border-[#7f5af0]/50 hover:shadow-lg hover:shadow-[#7f5af0]/10'
              }`}
            >
              <div className="flex items-start justify-between mb-2">
                <div className="flex items-center gap-2">
                  <motion.div
                    animate={note.processed ? { scale: [1, 1.2, 1] } : {}}
                    transition={{ duration: 0.5 }}
                  >
                    {note.processed ? (
                      <CheckCircle className="w-4 h-4 text-green-400 flex-shrink-0" />
                    ) : (
                      <motion.div
                        animate={{ rotate: 360 }}
                        transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
                      >
                        <AlertCircle className="w-4 h-4 text-yellow-400 flex-shrink-0" />
                      </motion.div>
                    )}
                  </motion.div>
                  <span className="text-xs text-[#e0e0ff]/50">
                    {note.processed ? 'Processed' : 'Pending'}
                  </span>
                </div>
                <div className="flex items-center gap-1 text-xs text-[#e0e0ff]/50">
                  <Clock className="w-3 h-3" />
                  {formatDate(note.timestamp)}
                </div>
              </div>

              <p className="text-[#e0e0ff]/80 text-sm leading-relaxed mb-3">
                {truncateText(note.content)}
              </p>

              {note.processed && (
                <motion.div 
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: 0.2 }}
                  className="flex flex-wrap gap-2"
                >
                  {note.sentiments?.slice(0, 2).map((sentiment, index) => (
                    <motion.span
                      key={index}
                      initial={{ scale: 0 }}
                      animate={{ scale: 1 }}
                      transition={{ delay: index * 0.1 }}
                      className="px-2 py-1 bg-blue-500/20 text-blue-300 text-xs rounded-full"
                    >
                      {sentiment}
                    </motion.span>
                  ))}
                  {note.resources_needed?.slice(0, 1).map((resource, index) => (
                    <motion.span
                      key={index}
                      initial={{ scale: 0 }}
                      animate={{ scale: 1 }}
                      transition={{ delay: 0.2 }}
                      className="px-2 py-1 bg-red-500/20 text-red-300 text-xs rounded-full"
                    >
                      needs: {resource}
                    </motion.span>
                  ))}
                  {(note.sentiments?.length || 0) + (note.resources_needed?.length || 0) > 3 && (
                    <motion.span 
                      initial={{ scale: 0 }}
                      animate={{ scale: 1 }}
                      transition={{ delay: 0.3 }}
                      className="px-2 py-1 bg-[#444466] text-[#e0e0ff]/50 text-xs rounded-full"
                    >
                      +{((note.sentiments?.length || 0) + (note.resources_needed?.length || 0)) - 3} more
                    </motion.span>
                  )}
                </motion.div>
              )}
            </motion.div>
          ))}
        </AnimatePresence>
      )}
    </div>
  );
};