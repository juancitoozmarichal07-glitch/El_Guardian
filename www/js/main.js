document.addEventListener('deviceready', onDeviceReady, false);

function onDeviceReady() {
    console.log('Dispositivo listo. Guardián operativo.');

    const chatBox = document.getElementById('chat-box');
    const userInput = document.getElementById('user-input');
    const sendButton = document.getElementById('send-button');

    // --- NUESTRA BASE DE DATOS EN MEMORIA ---
    let guardianData = {
        chat_history: [],
        reinos: []
    };

    // --- LÓGICA DE ALMACENAMIENTO MEJORADA ---
    function loadData() {
        NativeStorage.getItem('guardian_data', (data) => {
            if (data) {
                guardianData = data;
                // Asegurarse de que las propiedades existan para evitar errores
                if (!guardianData.chat_history) guardianData.chat_history = [];
                if (!guardianData.reinos) guardianData.reinos = [];

                // Cargar historial de chat
                if (guardianData.chat_history.length > 0) {
                    guardianData.chat_history.forEach(msg => addMessage(msg.text, msg.sender));
                } else {
                    initializeChat();
                }
            } else {
                initializeChat();
            }
        }, (error) => {
            console.log('No se encontraron datos, inicializando sistema.');
            initializeChat();
        });
    }

    function saveData() {
        NativeStorage.setItem('guardian_data', guardianData,
            () => console.log('Datos del Guardián guardados.'),
            (error) => console.error('Error al guardar datos:', error)
        );
    }

    function initializeChat() {
        const firstMessage = "Guardián: Estoy listo. Define tu próximo contrato o crea tu primer Reino.";
        addMessage(firstMessage, 'guardian-message');
        guardianData.chat_history.push({ text: firstMessage, sender: 'guardian-message' });
        saveData();
    }

    // --- LÓGICA DE INTERACCIÓN (SIN CAMBIOS) ---
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
        guardianData.chat_history.push({ text: userMessage, sender: 'user-message' });
        
        processCommand(userText); // El procesador de comandos ahora es más inteligente

        userInput.value = "";
        // No guardamos aquí, se guarda dentro de processCommand para asegurar consistencia
    }

    function addMessage(message, senderClass) {
        const messageElement = document.createElement('div');
        messageElement.className = `chat-message ${senderClass}`;
        messageElement.textContent = message;
        chatBox.appendChild(messageElement);
        chatBox.scrollTop = chatBox.scrollHeight;
    }

    // --- PROCESADOR DE COMANDOS MEJORADO (EL NUEVO CEREBRO) ---
    function processCommand(command) {
        let responseText = "";
        command = command.toLowerCase(); // Convertimos a minúsculas para facilitar la detección

        // Comando: crear reino [nombre]
        if (command.startsWith('crear reino ')) {
            const reinoName = command.substring(12).trim();
            if (reinoName && !guardianData.reinos.includes(reinoName)) {
                guardianData.reinos.push(reinoName);
                responseText = `Guardián: Reino "${reinoName}" creado con éxito. Tu universo se expande.`;
            } else if (guardianData.reinos.includes(reinoName)) {
                responseText = `Guardián: El Reino "${reinoName}" ya existe. Elige otro nombre.`;
            } else {
                responseText = "Guardián: Comando inválido. Usa: crear reino [nombre del reino].";
            }
        
        // Comando: listar reinos
        } else if (command.trim() === 'listar reinos') {
            if (guardianData.reinos.length > 0) {
                responseText = "Guardián: Estos son tus Reinos actuales:\n- " + guardianData.reinos.join('\n- ');
            } else {
                responseText = "Guardián: Aún no has creado ningún Reino. Tu universo espera ser definido. Usa 'crear reino [nombre]'.";
            }

        // Comando: contrato de duración (como antes)
        } else {
            const durationMatch = command.match(/(\d+)\s*(minutos|min|m)/i);
            if (durationMatch) {
                const duration = parseInt(durationMatch[1], 10);
                const task = command.replace(durationMatch[0], '').trim();
                responseText = `Guardián: Contrato aceptado. Tarea: '${task}'. Duración: ${duration} minutos. El tiempo empieza ahora.`;
            } else {
                responseText = "Guardián: Comando no reconocido. Prueba 'crear reino [nombre]', 'listar reinos' o define un contrato con duración.";
            }
        }
        
        addMessage(responseText, 'guardian-message');
        guardianData.chat_history.push({ text: responseText, sender: 'guardian-message' });
        saveData(); // Guardamos todos los datos (chat y reinos) después de cualquier operación
    }

    // --- PUNTO DE ENTRADA ---
    loadData();
}
