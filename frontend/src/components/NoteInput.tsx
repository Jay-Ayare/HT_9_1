import React, { useState } from 'react';
import { Plus, Upload, Loader2 } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

interface NoteInputProps {
  onSubmit: (notes: string[]) => void;
  isLoading: boolean;
}

export const NoteInput: React.FC<NoteInputProps> = ({ onSubmit, isLoading }) => {
  const [notes, setNotes] = useState<string[]>(['']);
  const [dragActive, setDragActive] = useState(false);

  const addNote = () => {
    setNotes([...notes, '']);
  };

  const updateNote = (index: number, value: string) => {
    const updated = [...notes];
    updated[index] = value;
    setNotes(updated);
  };

  const removeNote = (index: number) => {
    if (notes.length > 1) {
      const updated = notes.filter((_, i) => i !== index);
      setNotes(updated);
    }
  };

  const handleSubmit = () => {
    const validNotes = notes.filter(note => note.trim().length > 0);
    if (validNotes.length > 0) {
      onSubmit(validNotes);
    }
  };

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (!files) return;

    Array.from(files).forEach(file => {
      const reader = new FileReader();
      reader.onload = (e) => {
        const content = e.target?.result as string;
        setNotes(prev => [...prev.filter(n => n.trim()), content]);
      };
      reader.readAsText(file);
    });
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragActive(false);
    
    const files = Array.from(e.dataTransfer.files);
    files.forEach(file => {
      if (file.type === 'text/plain') {
        const reader = new FileReader();
        reader.onload = (e) => {
          const content = e.target?.result as string;
          setNotes(prev => [...prev.filter(n => n.trim()), content]);
        };
        reader.readAsText(file);
      }
    });
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setDragActive(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setDragActive(false);
  };

  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="space-y-6"
    >
      <div className="text-center">
        <h2 className="text-2xl font-bold text-[#e0e0ff] mb-2">Add Your Notes</h2>
        <p className="text-[#e0e0ff]/70">Share your thoughts and let AI find connections</p>
      </div>

      {/* File Upload Area */}
      <motion.div
        whileHover={{ scale: 1.02 }}
        transition={{ type: "spring", stiffness: 300 }}
        className={`relative border-2 border-dashed rounded-lg p-6 transition-all duration-200 ${
          dragActive 
            ? 'border-[#7f5af0] bg-[#7f5af0]/10' 
            : 'border-[#444466] hover:border-[#7f5af0]/50'
        }`}
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
      >
        <div className="text-center">
          <motion.div
            animate={{ y: [0, -5, 0] }}
            transition={{ duration: 2, repeat: Infinity, ease: "easeInOut" }}
          >
            <Upload className="mx-auto h-8 w-8 text-[#e0e0ff]/50 mb-2" />
          </motion.div>
          <p className="text-[#e0e0ff]/70 mb-2">Drag & drop text files here</p>
          <motion.label 
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className="inline-flex items-center px-4 py-2 bg-[#1a1a2e] hover:bg-[#7f5af0]/20 border border-[#444466] rounded-lg cursor-pointer transition-colors hover:shadow-lg hover:shadow-[#7f5af0]/20"
          >
            <Upload className="w-4 h-4 mr-2" />
            <span className="text-[#e0e0ff]">Choose Files</span>
            <input
              type="file"
              multiple
              accept=".txt"
              onChange={handleFileUpload}
              className="sr-only"
            />
          </motion.label>
        </div>
      </motion.div>

      {/* Manual Input */}
      <div className="space-y-4">
        <AnimatePresence>
          {notes.map((note, index) => (
            <motion.div 
              key={index} 
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 20 }}
              transition={{ duration: 0.3, delay: index * 0.1 }}
              className="relative"
            >
              <motion.textarea
                whileFocus={{ scale: 1.02 }}
                value={note}
                onChange={(e) => updateNote(index, e.target.value)}
                placeholder={`Note ${index + 1}: Share what's on your mind...`}
                className="w-full h-32 p-4 bg-[#1a1a2e] border border-[#444466] rounded-lg text-[#e0e0ff] placeholder-[#e0e0ff]/40 focus:border-[#7f5af0] focus:ring-1 focus:ring-[#7f5af0] focus:shadow-lg focus:shadow-[#7f5af0]/20 resize-none transition-all duration-200"
              />
              {notes.length > 1 && (
                <motion.button
                  whileHover={{ scale: 1.1, rotate: 90 }}
                  whileTap={{ scale: 0.9 }}
                  onClick={() => removeNote(index)}
                  className="absolute top-2 right-2 p-1 text-[#e0e0ff]/40 hover:text-red-400 transition-colors"
                  title="Remove note"
                >
                  ×
                </motion.button>
              )}
            </motion.div>
          ))}
        </AnimatePresence>

        <motion.button
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          onClick={addNote}
          className="w-full p-3 border-2 border-dashed border-[#444466] hover:border-[#7f5af0] text-[#e0e0ff]/70 hover:text-[#7f5af0] rounded-lg transition-all duration-200 flex items-center justify-center gap-2 hover:shadow-lg hover:shadow-[#7f5af0]/10"
        >
          <Plus className="w-4 h-4" />
          Add Another Note
        </motion.button>
      </div>

      <motion.button
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
        onClick={handleSubmit}
        disabled={isLoading || notes.every(n => !n.trim())}
        className="w-full py-3 px-6 bg-[#7f5af0] hover:bg-[#7f5af0]/80 disabled:opacity-50 disabled:cursor-not-allowed text-white font-medium rounded-lg transition-all duration-200 flex items-center justify-center gap-2 hover:shadow-lg hover:shadow-[#7f5af0]/30"
      >
        {isLoading ? (
          <>
            <Loader2 className="w-4 h-4 animate-spin" />
            Processing Notes...
          </>
        ) : (
          'Analyze Notes'
        )}
      </motion.button>
    </motion.div>
  );
};