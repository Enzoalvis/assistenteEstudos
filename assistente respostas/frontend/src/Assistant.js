import React, { useState } from 'react';
import axios from 'axios';
import './Assistant.css';

function Assistant() {
  const [inputText, setInputText] = useState('');
  const [messages, setMessages] = useState([]);
  const [listening, setListening] = useState(false);

  // Configuração do reconhecimento de voz (Web Speech API)
  let recognition;
  if ('webkitSpeechRecognition' in window) {
      recognition = new window.webkitSpeechRecognition();
      recognition.continuous = false;
      recognition.lang = 'pt-BR';
      recognition.interimResults = false;
      recognition.maxAlternatives = 1;
      recognition.onresult = (event) => {
          const transcript = event.results[0][0].transcript;
          setInputText(transcript);
          sendMessage(transcript);
          setListening(false);
      };
      recognition.onerror = (event) => {
          console.error(event.error);
          setListening(false);
      };
  }

  const startListening = () => {
      if (recognition) {
          setListening(true);
          recognition.start();
      }
  };

  const sendMessage = async (text) => {
      setMessages((prev) => [...prev, { sender: 'user', text }]);
      try {
          const response = await axios.post('http://localhost:5000/api/assistant', { input: text });
          setMessages((prev) => [...prev, { sender: 'assistant', text: response.data.response }]);
      } catch (error) {
          console.error(error);
      }
  };

  const handleSubmit = (e) => {
      e.preventDefault();
      if (inputText.trim() !== '') {
          sendMessage(inputText);
          setInputText('');
      }
  };

  return (
      <div className="assistant-container">
          <div className="messages">
              {messages.map((msg, index) => (
                  <div key={index} className={`message ${msg.sender}`}>
                      {msg.text}
                  </div>
              ))}
          </div>
          <form onSubmit={handleSubmit} className="input-area">
              <input
                  type="text"
                  value={inputText}
                  onChange={(e) => setInputText(e.target.value)}
                  placeholder="Digite sua pergunta..."
              />
              <button type="submit">Enviar</button>
              <button type="button" onClick={startListening}>
                  {listening ? 'Escutando...' : 'Falar'}
              </button>
          </form>
      </div>
  );
}

export default Assistant;
