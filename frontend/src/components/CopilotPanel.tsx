import React, { useState, useRef, useEffect } from 'react';
import { useAppDispatch, useAppSelector } from '../store';
import { addMessage, setLoading } from '../store/chatSlice';
import { setEntireState } from '../store/formSlice';
import {
  Bot,
  Send,
  Upload,
  Sparkles,
  Wrench,
  Paperclip,
  Loader2,
  FileCode,
  FileText,
} from 'lucide-react';
import axios from 'axios';

export const CopilotPanel: React.FC = () => {
  const dispatch = useAppDispatch();
  const messages = useAppSelector((state) => state.chat.messages);
  const isLoading = useAppSelector((state) => state.chat.isLoading);
  const currentFormState = useAppSelector((state) => state.form);

  const [inputPrompt, setInputPrompt] = useState('');
  const fileInputRef = useRef<HTMLInputElement>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const handleSendMessage = async () => {
    if (!inputPrompt.trim() || isLoading) return;

    const userText = inputPrompt.trim();
    setInputPrompt('');

    // Dispatch user message to Redux chat state
    dispatch(
      addMessage({
        sender: 'user',
        message: userText,
      })
    );

    dispatch(setLoading(true));

    try {
      const response = await axios.post('/api/copilot/process', {
        user_prompt: userText,
        current_form_state: currentFormState,
      });

      const data = response.data;

      // 1. Update Redux chat history
      dispatch(
        addMessage({
          sender: 'copilot',
          message: data.chat_message,
          tool_used: data.tool_used,
        })
      );

      // 2. Synchronize left form state & risk assessment
      if (data.form_state || data.risk_assessment) {
        dispatch(
          setEntireState({
            formState: data.form_state,
            riskState: data.risk_assessment,
          })
        );
      }
    } catch (err: any) {
      console.error('Copilot processing error:', err);
      dispatch(
        addMessage({
          sender: 'copilot',
          message: `Error processing request: ${err.response?.data?.detail || err.message}`,
          tool_used: 'error_handler',
        })
      );
    } finally {
      dispatch(setLoading(false));
    }
  };

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (!files || files.length === 0) return;

    const file = files[0];
    dispatch(setLoading(true));

    // Dispatch user upload notice to chat
    dispatch(
      addMessage({
        sender: 'user',
        message: `Uploaded document: **${file.name}** (${(file.size / 1024).toFixed(1)} KB)`,
      })
    );

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post('/api/copilot/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      const data = response.data;

      // 1. Update Redux chat history
      dispatch(
        addMessage({
          sender: 'copilot',
          message: data.chat_message,
          tool_used: data.tool_used || 'document_extraction_tool',
        })
      );

      // 2. Synchronize left form state & risk assessment
      if (data.form_state || data.risk_assessment) {
        dispatch(
          setEntireState({
            formState: data.form_state,
            riskState: data.risk_assessment,
          })
        );
      }
    } catch (err: any) {
      console.error('File upload error:', err);
      dispatch(
        addMessage({
          sender: 'copilot',
          message: `File processing error: ${err.response?.data?.detail || err.message}`,
          tool_used: 'upload_error',
        })
      );
    } finally {
      dispatch(setLoading(false));
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <div
      className="copilot-panel-container"
      style={{
        background: 'var(--bg-card)',
        borderRadius: 'var(--radius-lg)',
        border: '1px solid var(--border-light)',
        padding: '1.5rem',
        display: 'flex',
        flexDirection: 'column',
        gap: '1rem',
        boxShadow: 'var(--shadow-md)',
        height: '100%',
      }}
    >
      {/* Header */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          paddingBottom: '1rem',
          borderBottom: '1px solid var(--border-light)',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <div
            style={{
              background: 'linear-gradient(135deg, rgba(14, 165, 233, 0.2) 0%, rgba(20, 184, 166, 0.2) 100%)',
              padding: '0.55rem',
              borderRadius: 'var(--radius-sm)',
              display: 'flex',
              alignItems: 'center',
              border: '1px solid rgba(14, 165, 233, 0.3)',
            }}
          >
            <Bot size={22} color="#38bdf8" />
          </div>
          <div>
            <h2 style={{ fontSize: '1.15rem', fontWeight: 700, color: 'var(--text-main)' }}>
              AIVOA Copilot
            </h2>
            <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
              Groq Llama-3.3-70B & Gemma-2 Agent Assistant
            </p>
          </div>
        </div>

        {/* Upload Button */}
        <div>
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileUpload}
            style={{ display: 'none' }}
            accept=".pdf,.txt,.eml,.msg"
          />
          <button
            onClick={() => fileInputRef.current?.click()}
            disabled={isLoading}
            style={{
              background: 'rgba(14, 165, 233, 0.12)',
              color: '#38bdf8',
              border: '1px solid rgba(14, 165, 233, 0.3)',
              borderRadius: 'var(--radius-sm)',
              padding: '0.45rem 0.85rem',
              fontSize: '0.8rem',
              fontWeight: 600,
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '0.4rem',
              transition: 'all 0.2s ease',
            }}
          >
            <Upload size={14} /> Upload Complaint File
          </button>
        </div>
      </div>

      {/* Message List */}
      <div
        style={{
          flex: 1,
          overflowY: 'auto',
          display: 'flex',
          flexDirection: 'column',
          gap: '1rem',
          paddingRight: '0.4rem',
          minHeight: '350px',
          maxHeight: '520px',
        }}
      >
        {messages.map((msg) => (
          <div
            key={msg.id}
            style={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: msg.sender === 'user' ? 'flex-end' : 'flex-start',
            }}
          >
            <div
              style={{
                maxWidth: '85%',
                padding: '0.85rem 1.1rem',
                borderRadius:
                  msg.sender === 'user'
                    ? '14px 14px 2px 14px'
                    : '14px 14px 14px 2px',
                background:
                  msg.sender === 'user'
                    ? 'linear-gradient(135deg, #0284c7 0%, #0369a1 100%)'
                    : 'var(--bg-accent)',
                color: 'var(--text-main)',
                fontSize: '0.88rem',
                lineHeight: 1.5,
                border:
                  msg.sender === 'user'
                    ? '1px solid rgba(56, 189, 248, 0.4)'
                    : '1px solid var(--border-light)',
                boxShadow: 'var(--shadow-sm)',
              }}
            >
              {/* Message Header Badge */}
              <div
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.4rem',
                  fontSize: '0.7rem',
                  color: msg.sender === 'user' ? '#e0f2fe' : 'var(--text-muted)',
                  marginBottom: '0.3rem',
                }}
              >
                {msg.sender === 'user' ? (
                  <span>You</span>
                ) : (
                  <span style={{ display: 'flex', alignItems: 'center', gap: '0.25rem', color: '#38bdf8', fontWeight: 600 }}>
                    <Sparkles size={12} /> Copilot Agent
                  </span>
                )}

                <span>• {msg.timestamp}</span>

                {msg.tool_used && (
                  <span
                    style={{
                      background: 'rgba(255, 255, 255, 0.1)',
                      padding: '0.1rem 0.4rem',
                      borderRadius: 'var(--radius-sm)',
                      fontSize: '0.65rem',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '0.2rem',
                    }}
                  >
                    <Wrench size={10} /> {msg.tool_used}
                  </span>
                )}
              </div>

              {/* Message Text */}
              <div style={{ whiteSpace: 'pre-wrap' }}>{msg.message}</div>
            </div>
          </div>
        ))}

        {/* Loading Spinner */}
        {isLoading && (
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: '#38bdf8', fontSize: '0.85rem' }}>
            <Loader2 size={16} className="animate-spin" style={{ animation: 'spin 1s linear infinite' }} />
            <span>Agent executing workflow (Groq Llama-3.3)...</span>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div
        style={{
          display: 'flex',
          gap: '0.5rem',
          background: 'var(--bg-dark)',
          padding: '0.5rem',
          borderRadius: 'var(--radius-md)',
          border: '1px solid var(--border-light)',
          alignItems: 'center',
        }}
      >
        <button
          onClick={() => fileInputRef.current?.click()}
          title="Attach PDF or email file"
          style={{
            background: 'transparent',
            border: 'none',
            color: 'var(--text-muted)',
            cursor: 'pointer',
            padding: '0.4rem',
            borderRadius: 'var(--radius-sm)',
            display: 'flex',
            alignItems: 'center',
          }}
        >
          <Paperclip size={18} />
        </button>

        <input
          type="text"
          value={inputPrompt}
          onChange={(e) => setInputPrompt(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Log complaint, edit fields e.g., 'Edit batch number to B-999'..."
          disabled={isLoading}
          style={{
            flex: 1,
            background: 'transparent',
            border: 'none',
            outline: 'none',
            color: 'var(--text-main)',
            fontSize: '0.88rem',
            fontFamily: 'var(--font-family)',
          }}
        />

        <button
          onClick={handleSendMessage}
          disabled={isLoading || !inputPrompt.trim()}
          style={{
            background: inputPrompt.trim() ? 'var(--primary-600)' : 'var(--bg-card-hover)',
            color: '#ffffff',
            border: 'none',
            borderRadius: 'var(--radius-sm)',
            padding: '0.55rem 0.9rem',
            cursor: inputPrompt.trim() && !isLoading ? 'pointer' : 'not-allowed',
            display: 'flex',
            alignItems: 'center',
            gap: '0.3rem',
            fontWeight: 600,
            fontSize: '0.8rem',
            transition: 'all 0.2s ease',
          }}
        >
          <Send size={14} /> Send
        </button>
      </div>

      {/* Quick Prompts Bar */}
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.4rem', paddingTop: '0.2rem' }}>
        <span style={{ fontSize: '0.7rem', color: 'var(--text-subtle)', alignSelf: 'center' }}>
          Quick prompts:
        </span>
        <button
          onClick={() => setInputPrompt('Log a complaint: Batch A123 of Paracetamol 500mg has discolored tablets.')}
          style={chipStyle}
        >
          <FileText size={10} /> Log Paracetamol Complaint
        </button>
        <button
          onClick={() => setInputPrompt('Edit batch number to LOT-9999B')}
          style={chipStyle}
        >
          <FileCode size={10} /> Edit Batch Number
        </button>
      </div>
    </div>
  );
};

const chipStyle: React.CSSProperties = {
  background: 'rgba(255, 255, 255, 0.05)',
  border: '1px solid var(--border-light)',
  color: 'var(--text-muted)',
  borderRadius: 'var(--radius-full)',
  padding: '0.2rem 0.55rem',
  fontSize: '0.7rem',
  cursor: 'pointer',
  display: 'inline-flex',
  alignItems: 'center',
  gap: '0.25rem',
};
