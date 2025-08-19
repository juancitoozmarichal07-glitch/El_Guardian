// --- LÓGICA VISUAL (SE EJECUTA INMEDIATAMENTE) ---

// Espera a que el contenido de la página esté cargado para encontrar los elementos.
document.addEventListener('DOMContentLoaded', (event) => {
    console.log('DOM cargado. Inicializando interfaz...');

    const chatBox = document.getElementById('chat-box');
    const userInput = document.getElementById('user-input');
    const sendButton = document.getElementById('send-button');

    // Comprobamos que los elementos existen antes de usarlos
    if (!chatBox || !userInput || !sendButton) {
        console.error('Error crítico: No se encontraron los elementos de la interfaz.');
        alert('Error crítico: La interfaz no se pudo cargar.');
        return;
    }

    let chatHistory = [];

    // --- LÓGICA DE MEMORIA (ESPERA AL DISPOSITIVO) ---

    // Escuchamos el evento 'deviceready' para la lógica de plugins
    document.addEventListener('deviceready', onDeviceReady, false);

    function onDeviceReady() {
        console.log('Dispositivo listo. Intentando cargar historial...');
        loadHistory();
    }

    function loadHistory() {
        // Usamos un try/catch para asegurarnos de que si NativeStorage no existe, no se rompa todo
        try {
            NativeStorage.getItem('chat_history', (history) => {
                if (history && history.length > 0) {
                    chatHistory = history;
                    // Limpiamos el chat antes de cargar el historial para evitar duplicados
                    chatBox.innerHTML = ''; 
                    chatHistory.forEach(msg => addMessage(msg.text, msg.sender));
                    console.log('Historial cargado con éxito.');
                }
            }, (error) => {
                // Si no hay historial, no hacemos nada, ya se mostró el saludo inicial
                console.log('No se encontró historial, se mantiene el saludo inicial.');
            });
        } catch (e) {
            console.error('NativeStorage no está disponible. La memoria no funcionará.', e);
            // Opcional: Mostrar un mensaje al usuario
            // addMessage('Guardián: Advertencia, la memoria persistente ha fallado.', 'guardian-message');
        }
    }

    function saveHistory() {
        try {
            NativeStorage.setItem('chat_history', chatHistory, 
                () => console.log('Historial guardado.'),
                (error) => console.error('Error al guardar historial:', error)
            );
        } catch (e) {
            console.error('NativeStorage no está disponible. No se puede guardar.', e);
        }
    }

    // --- LÓGICA DE INTERACCIÓN (COMÚN A AMBOS) ---

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
    }

    // --- SALUDO INICIAL (SE MUESTRA SIEMPRE AL PRINCIPIO) ---
    const firstMessage = "Guardián: Estoy listo. Define tu próximo contrato.";
    addMessage(firstMessage, 'guardian-message');
    chatHistory.push({ text: firstMessage, sender: 'guardian-message' });
    
});
