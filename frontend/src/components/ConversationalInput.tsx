import React, { useState, useRef } from 'react';

interface ConversationalInputProps {
  onSubmit: (input: string) => void;
  isLoading?: boolean;
  placeholder?: string;
}

const ConversationalInput: React.FC<ConversationalInputProps> = ({
  onSubmit,
  isLoading = false,
  placeholder = "Tell me about the person you're shopping for..."
}) => {
  const [input, setInput] = useState('');
  const [isFocused, setIsFocused] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (input.trim() && !isLoading) {
      onSubmit(input.trim());
      setInput('');
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const adjustTextareaHeight = () => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
    }
  };

  React.useEffect(() => {
    adjustTextareaHeight();
  }, [input]);

  const examplePrompts = [
    "I need a birthday gift for my brother who loves gaming",
    "Looking for an anniversary gift for my wife who enjoys cooking",
    "Help me find a gift for my colleague who is into fitness",
    "Need a gift for my teenage daughter who likes art and music"
  ];

  const handleExampleClick = (prompt: string) => {
    setInput(prompt);
    if (textareaRef.current) {
      textareaRef.current.focus();
    }
  };

  return (
    <div className="w-full max-w-4xl mx-auto">
      {/* Example Prompts */}
      <div className="mb-4">
        <p className="text-sm text-gray-600 mb-2">Try these examples:</p>
        <div className="flex flex-wrap gap-2">
          {examplePrompts.map((prompt, index) => (
            <button
              key={index}
              onClick={() => handleExampleClick(prompt)}
              className="px-3 py-1 bg-gray-100 text-gray-700 text-sm rounded-full hover:bg-gray-200 transition-colors"
            >
              {prompt}
            </button>
          ))}
        </div>
      </div>

      {/* Input Form */}
      <form onSubmit={handleSubmit} className="relative">
        <div className={`relative border rounded-lg transition-all ${
          isFocused ? 'border-blue-500 shadow-lg' : 'border-gray-300'
        } bg-white`}>
          <textarea
            ref={textareaRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            onFocus={() => setIsFocused(true)}
            onBlur={() => setIsFocused(false)}
            placeholder={placeholder}
            disabled={isLoading}
            className="w-full px-4 py-3 pr-12 border-0 rounded-lg resize-none focus:outline-none focus:ring-0 disabled:opacity-50"
            rows={1}
            style={{ minHeight: '48px', maxHeight: '120px' }}
          />
          
          {/* Submit Button */}
          <button
            type="submit"
            disabled={!input.trim() || isLoading}
            className="absolute right-2 bottom-2 p-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {isLoading ? (
              <svg className="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 0112 15c-2.146 0-4.1-.85-5.543-2.236l1.414-1.414A5.976 5.976 0 0012 13a5.976 5.976 0 004.129-1.65l1.414 1.414A7.962 7.962 0 0112 15v4z" />
              </svg>
            ) : (
              <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
              </svg>
            )}
          </button>
        </div>

        {/* Character Count */}
        {input.length > 0 && (
          <div className="absolute bottom-2 right-2 text-xs text-gray-400">
            {input.length} characters
          </div>
        )}
      </form>

      {/* Tips */}
      <div className="mt-4 text-sm text-gray-600">
        <p className="font-medium mb-1">💡 Tips for better recommendations:</p>
        <ul className="space-y-1 text-xs">
          <li>• Mention the recipient's age, gender, and interests</li>
          <li>• Specify the occasion (birthday, anniversary, etc.)</li>
          <li>• Include your budget range</li>
          <li>• Mention any constraints or preferences</li>
          <li>• Describe your relationship with the recipient</li>
        </ul>
      </div>
    </div>
  );
};

export default ConversationalInput;
