document.addEventListener('deviceready', onDeviceReady, false);

function onDeviceReady() {
    console.log('Running cordova-' + cordova.platformId + '@' + cordova.version);
    console.log('Dispositivo listo. Guardián operativo.');

    const chatBox = document.getElementById('chat-box');
    const userInput = document.getElementById('user-input');
    const sendButton = document.getElementById('send-button');

    let chatHistory = [];

    function loadHistory() {
        NativeStorage.getItem('chat_history', (history) => {
            if (history && history.length > 0) {
                chatHistory = history;
                chatHistory.forEach(msg => addMessage(msg.text, msg.sender));
            } else {
                initializeChat();
            }
        }, (error) => {
            console.log('No se encontró historial, inicializando chat.');
            initializeChat();
        });
    }

    function saveHistory() {
        NativeStorage.setItem('chat_history', chatHistory, 
            () => console.log('Historial guardado.'),
            (error) => console.error('Error al guardar historial:', error)
        );
    }

    function initializeChat() {
        const firstMessage = "Guardián: Estoy listo. Define tu próximo contrato.";
        addMessage(firstMessage, 'guardian-message');
        chatHistory.push({ text: firstMessage, sender: 'guardian-message' });
        saveHistory();
    }

    sendButton.addEventListener('click', handleUserInput);
    userInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            handleUserInput();
        }
    });

    function handleUserInput() {
        const userText = userInput.value.trim();
        if (userText === "") return;

        const userMessage = `Tú: ${userText}`;
        addMessage(userMessage, 'user-message');
        chatHistory.push({ text: userMessage, sender: 'user-message' });
        
        processCommand(userText);

        userInput.value = "";
        saveHistory();
    }

    function addMessage(message, senderClass) {
        const messageElement = document.createElement('div');
        messageElement.className = `chat-message ${senderClass}`;
        messageElement.textContent = message;
        chatBox.appendChild(messageElement);
        chatBox.scrollTop = chatBox.scrollHeight;
    }

    function processCommand(command) {
        const durationMatch = command.match(/(\d+)\s*(minutos|min|m)/i);
        let responseText = "";

        if (durationMatch) {
            const duration = parseInt(durationMatch[1], 10);
            const task = command.replace(durationMatch[0], '').trim();
            responseText = `Guardián: Contrato aceptado. Tarea: '${task}'. Duración: ${duration} minutos. El tiempo empieza ahora.`;
        } else {
            responseText = "Guardián: No he reconocido una duración. Ejemplo: 'Leer sobre IA por 30 minutos'.";
        }
        
        addMessage(responseText, 'guardian-message');
        chatHistory.push({ text: responseText, sender: 'guardian-message' });
        saveHistory();
    }

    // --- PUNTO DE ENTRADA ---
    loadHistory();
}
