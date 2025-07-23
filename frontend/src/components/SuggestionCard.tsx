import React, { useState } from 'react';
import { Suggestion } from '../types';
import { Lightbulb, ArrowRight, ChevronDown, ChevronUp } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

// Function to convert markdown formatting to JSX
const parseMarkdown = (text: string): React.ReactNode => {
  // Split by double line breaks first to create paragraphs
  const paragraphs = text.split(/\n\n+/);
  
  return (
    <>
      {paragraphs.map((paragraph, paragraphIndex) => {
        // Handle both bold and italic within each paragraph
        const processedText = paragraph
          .split(/(\*\*.*?\*\*|\*.*?\*)/)
          .map((part, index) => {
            if (part.startsWith('**') && part.endsWith('**')) {
              // Bold text
              return (
                <strong key={`bold-${paragraphIndex}-${index}`} className="font-semibold text-[#e0e0ff]">
                  {part.slice(2, -2)}
                </strong>
              );
            } else if (part.startsWith('*') && part.endsWith('*') && !part.startsWith('**')) {
              // Italic text (but not bold)
              return (
                <em key={`italic-${paragraphIndex}-${index}`} className="italic text-[#e0e0ff]/80">
                  {part.slice(1, -1)}
                </em>
              );
            } else {
              // Regular text - handle single line breaks within paragraphs
              return part.split('\n').map((line, lineIndex, lines) => (
                <React.Fragment key={`line-${paragraphIndex}-${index}-${lineIndex}`}>
                  {line}
                  {lineIndex < lines.length - 1 && <br />}
                </React.Fragment>
              ));
            }
          })
          .filter(part => part !== ''); // Remove empty strings
        
        return (
          <p key={`paragraph-${paragraphIndex}`} className="mb-3 last:mb-0">
            {processedText}
          </p>
        );
      })}
    </>
  );
};

interface SuggestionCardProps {
  suggestion: Suggestion;
}

export const SuggestionCard: React.FC<SuggestionCardProps> = ({ suggestion }) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const [isTyping, setIsTyping] = useState(false);
  const [displayedText, setDisplayedText] = useState('');

  React.useEffect(() => {
    if (isExpanded && !isTyping) {
      setIsTyping(true);
      setDisplayedText('');
      
      const text = suggestion.suggestion;
      let index = 0;
      
      const typeInterval = setInterval(() => {
        if (index < text.length) {
          setDisplayedText(text.slice(0, index + 1));
          index++;
        } else {
          setIsTyping(false);
          clearInterval(typeInterval);
        }
      }, 30);
      
      return () => clearInterval(typeInterval);
    }
  }, [isExpanded, suggestion.suggestion]);

  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{ scale: 1.02, y: -2 }}
      className="bg-gradient-to-r from-[#7f5af0]/10 to-blue-500/10 rounded-lg border border-[#7f5af0]/30 overflow-hidden hover:border-[#7f5af0]/50 hover:shadow-lg hover:shadow-[#7f5af0]/20 transition-all duration-200"
    >
      <motion.div 
        whileHover={{ backgroundColor: 'rgba(127, 90, 240, 0.05)' }}
        onClick={() => setIsExpanded(!isExpanded)}
        className="flex items-center justify-between p-4 cursor-pointer transition-colors"
      >
        <div className="flex items-center gap-3">
          <motion.div 
            whileHover={{ rotate: 15, scale: 1.1 }}
            className="w-8 h-8 bg-gradient-to-r from-[#7f5af0] to-blue-400 rounded-full flex items-center justify-center"
          >
            <Lightbulb className="w-4 h-4 text-white" />
          </motion.div>
          <div>
            <h4 className="font-medium text-[#e0e0ff]">Connection Opportunity</h4>
            <div className="flex items-center gap-2 text-sm text-[#e0e0ff]/70">
              <motion.span 
                whileHover={{ scale: 1.05 }}
                className="px-2 py-1 bg-red-500/20 text-red-300 rounded text-xs"
              >
                {suggestion.need}
              </motion.span>
              <motion.div
                animate={{ x: [0, 5, 0] }}
                transition={{ duration: 1.5, repeat: Infinity }}
              >
                <ArrowRight className="w-3 h-3" />
              </motion.div>
              <motion.span 
                whileHover={{ scale: 1.05 }}
                className="px-2 py-1 bg-green-500/20 text-green-300 rounded text-xs"
              >
                {suggestion.availability}
              </motion.span>
            </div>
          </div>
        </div>
        <motion.div 
          animate={{ rotate: isExpanded ? 180 : 0 }}
          transition={{ duration: 0.2 }}
          className="text-[#e0e0ff]/50"
        >
          <ChevronDown className="w-4 h-4" />
        </motion.div>
      </motion.div>

      <AnimatePresence>
        {isExpanded && (
          <motion.div 
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.3 }}
            className="px-4 pb-4 overflow-hidden"
          >
            <motion.div 
              initial={{ y: -10 }}
              animate={{ y: 0 }}
              className="bg-[#0f0f1a] p-4 rounded-lg border border-[#444466] backdrop-blur-sm"
            >
              <div className="text-[#e0e0ff]/90 leading-relaxed">
                {parseMarkdown(displayedText)}
                {isTyping && (
                  <motion.span
                    animate={{ opacity: [1, 0] }}
                    transition={{ duration: 0.5, repeat: Infinity }}
                    className="inline-block w-2 h-5 bg-[#7f5af0] ml-1"
                  />
                )}
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
};