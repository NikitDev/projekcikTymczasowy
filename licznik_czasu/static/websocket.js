// Tworzenie obiektu WebSocket
let socket;

// Funkcja do nawiązywania połączenia WebSocket
function connectWebSocket() {
  // Sprawdź, czy WebSocket jest już otwarty, aby uniknąć nawiązywania kolejnych połączeń
  if (socket && socket.readyState === WebSocket.OPEN) {
    console.log('Połączenie WebSocket jest już otwarte.');
    return;
  }

  // Nawiązanie połączenia WebSocket
  socket = new WebSocket('ws://127.0.0.1:8000/ws/');
  console.log("OHO");
  // Obsługa zdarzenia otwarcia połączenia
  socket.onopen = function(event) {
    console.log('Połączenie WebSocket zostało nawiązane.');
  };

  // Obsługa zdarzenia otrzymania wiadomości
  socket.onmessage = function(event) {
    const message = JSON.parse(event.data);
    // Obsługa otrzymanej wiadomości (ping)
  };

  // Obsługa zdarzenia zamknięcia połączenia
  socket.onclose = function(event) {
    console.log('Połączenie WebSocket zostało zamknięte.');
  };

  // Obsługa zdarzenia błędu połączenia
  socket.onerror = function(event) {
    console.error('Wystąpił błąd połączenia WebSocket:', event);
  };
}

// Funkcja do wysyłania wiadomości (ping)
function sendPing() {
  if (!socket || socket.readyState !== WebSocket.OPEN) {
    console.log('Połączenie WebSocket nie jest otwarte.');
    return;
  }

  const message = { type: 'ping' };
  socket.send(JSON.stringify(message));
}

// Event listener dla przycisku
document.addEventListener('DOMContentLoaded', function() {
    const connectButton = document.getElementById('test');
    connectButton.addEventListener('click', connectWebSocket);
});
//$("#test").click(function() {
//        connectWebSocket();
//        });