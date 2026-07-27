import { createSlice, type PayloadAction } from '@reduxjs/toolkit';

export interface ChatMessage {
  id: string;
  sender: 'user' | 'copilot';
  message: string;
  timestamp: string;
  tool_used?: string | null;
}

export interface ChatState {
  messages: ChatMessage[];
  isLoading: boolean;
}

const initialState: ChatState = {
  messages: [
    {
      id: 'welcome-msg',
      sender: 'copilot',
      message: 'Hello! I am AIVOA Copilot. Upload a complaint document (PDF/email) or describe a product quality event to populate the complaint intake form.',
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      tool_used: 'system_greeting',
    },
  ],
  isLoading: false,
};

export const chatSlice = createSlice({
  name: 'chat',
  initialState,
  reducers: {
    addMessage: (state, action: PayloadAction<Omit<ChatMessage, 'id' | 'timestamp'> & { id?: string; timestamp?: string }>) => {
      const msg: ChatMessage = {
        id: action.payload.id || `msg-${Date.now()}-${Math.random().toString(36).substr(2, 4)}`,
        sender: action.payload.sender,
        message: action.payload.message,
        timestamp: action.payload.timestamp || new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        tool_used: action.payload.tool_used || null,
      };
      state.messages.push(msg);
    },
    setLoading: (state, action: PayloadAction<boolean>) => {
      state.isLoading = action.payload;
    },
    clearChat: (state) => {
      state.messages = [];
    },
  },
});

export const { addMessage, setLoading, clearChat } = chatSlice.actions;

export default chatSlice.reducer;
