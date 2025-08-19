document.addEventListener('deviceready', onDeviceReady, false);

function onDeviceReady() {
    console.log('Dispositivo listo. Guardián operativo.');

    const chatBox = document.getElementById('chat-box');
    const userInput = document.getElementById('user-input');
    const sendButton = document.getElementById('send-button');

    // --- NUESTRA BASE DE DATOS EVOLUCIONADA ---
    let guardianData = {
        chat_history: [],
        reinos: [], // Ahora es un array de objetos complejos
        activeContext: { // Para saber dónde estamos trabajando
            reino: null,
            templo: null
        }
    };

    // --- LÓGICA DE ALMACENAMIENTO ---
    function loadData() {
        // Usamos window.NativeStorage para ser explícitos
        window.NativeStorage.getItem('guardian_data', (data) => {
            if (data) {
                guardianData = data;
                // Asegurarse de que las propiedades existan para evitar errores tras una actualización
                if (!guardianData.chat_history) guardianData.chat_history = [];
                if (!guardianData.reinos) guardianData.reinos = [];
                if (!guardianData.activeContext) guardianData.activeContext = { reino: null, templo: null };

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
        window.NativeStorage.setItem('guardian_data', guardianData,
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

    // --- LÓGICA DE INTERACCIÓN ---
    sendButton.addEventListener('click', handleUserInput);
    userInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            handleUserInput();
        }
    });

    function handleUserInput() {
        const userText = userInput.value.trim();
        if (userText === "") return;

        // Añadimos el prefijo "Tú:" para consistencia visual
        const userMessageText = `Tú: ${userText}`;
        addMessage(userMessageText, 'user-message');
        guardianData.chat_history.push({ text: userMessageText, sender: 'user-message' });
        
        processCommand(userText);

        userInput.value = "";
    }

    function addMessage(message, senderClass) {
        const messageElement = document.createElement('div');
        messageElement.className = `chat-message ${senderClass}`;
        // Usamos innerText para prevenir problemas de formato con los saltos de línea
        messageElement.innerText = message;
        chatBox.appendChild(messageElement);
        chatBox.scrollTop = chatBox.scrollHeight;
    }

    // --- PROCESADOR DE COMANDOS (EL CEREBRO DEL GUARDIÁN) ---
    function processCommand(command) {
        let responseText = "";
        const lowerCaseCommand = command.toLowerCase();

        // Comando: crear reino [nombre]
        if (lowerCaseCommand.startsWith('crear reino ')) {
            const reinoName = command.substring(12).trim();
            const reinoExists = guardianData.reinos.some(reino => reino.name.toLowerCase() === reinoName.toLowerCase());

            if (reinoName && !reinoExists) {
                const nuevoReino = {
                    name: reinoName,
                    templos: []
                };
                guardianData.reinos.push(nuevoReino);
                responseText = `Guardián: Reino "${reinoName}" creado con éxito. Tu universo se expande.`;
            } else if (reinoExists) {
                responseText = `Guardián: El Reino "${reinoName}" ya existe. Elige otro nombre.`;
            } else {
                responseText = "Guardián: Comando inválido. Usa: crear reino [nombre del reino].";
            }
        
        // Comando: listar reinos
        } else if (lowerCaseCommand.trim() === 'listar reinos') {
            if (guardianData.reinos.length > 0) {
                const reinoNames = guardianData.reinos.map(reino => reino.name);
                responseText = "Guardián: Estos son tus Reinos actuales:\n- " + reinoNames.join('\n- ');
            } else {
                responseText = "Guardián: Aún no has creado ningún Reino. Usa 'crear reino [nombre]'.";
            }

        // Comando: crear templo [nombreTemplo] en [nombreReino]
        } else if (lowerCaseCommand.startsWith('crear templo ')) {
            const match = command.match(/crear templo (.*) en (.*)/i);
            if (match) {
                const temploName = match[1].trim();
                const reinoName = match[2].trim();
                const reinoTarget = guardianData.reinos.find(r => r.name.toLowerCase() === reinoName.toLowerCase());

                if (reinoTarget) {
                    const temploExists = reinoTarget.templos.some(t => t.name.toLowerCase() === temploName.toLowerCase());
                    if (!temploExists) {
                        const nuevoTemplo = {
                            name: temploName,
                            level: 1,
                            contracts: []
                        };
                        reinoTarget.templos.push(nuevoTemplo);
                        responseText = `Guardián: Templo "${temploName}" erigido con éxito en el Reino de "${reinoName}".`;
                    } else {
                        responseText = `Guardián: El Templo "${temploName}" ya existe en el Reino de "${reinoName}".`;
                    }
                } else {
                    responseText = `Guardián: No se encontró el Reino "${reinoName}".`;
                }
            } else {
                responseText = "Guardián: Comando inválido. Usa: crear templo [nombre] en [reino].";
            }

        // Comando: listar templos en [nombreReino]
        } else if (lowerCaseCommand.startsWith('listar templos en ')) {
            const reinoName = command.substring(18).trim();
            const reinoTarget = guardianData.reinos.find(r => r.name.toLowerCase() === reinoName.toLowerCase());

            if (reinoTarget) {
                if (reinoTarget.templos.length > 0) {
                    const temploNames = reinoTarget.templos.map(t => `${t.name} (Nivel ${t.level})`);
                    responseText = `Guardián: Los Templos en el Reino de "${reinoName}" son:\n- ` + temploNames.join('\n- ');
                } else {
                    responseText = `Guardián: El Reino de "${reinoName}" aún no tiene Templos.`;
                }
            } else {
                responseText = `Guardián: No se encontró el Reino "${reinoName}".`;
            }
            
        // Comando: entrar en templo [nombreTemplo] de [nombreReino]
        } else if (lowerCaseCommand.startsWith('entrar en templo ')) {
            const match = command.match(/entrar en templo (.*) de (.*)/i);
            if (match) {
                const temploName = match[1].trim();
                const reinoName = match[2].trim();
                const reinoTarget = guardianData.reinos.find(r => r.name.toLowerCase() === reinoName.toLowerCase());

                if (reinoTarget) {
                    const temploTarget = reinoTarget.templos.find(t => t.name.toLowerCase() === temploName.toLowerCase());
                    if (temploTarget) {
                        guardianData.activeContext.reino = reinoTarget.name;
                        guardianData.activeContext.templo = temploTarget.name;
                        responseText = `Guardián: Has entrado al Templo "${temploTarget.name}" en el Reino de "${reinoTarget.name}". Tu foco está establecido.`;
                    } else {
                        responseText = `Guardián: No se encontró el Templo "${temploName}" en ese Reino.`;
                    }
                } else {
                    responseText = `Guardián: No se encontró el Reino "${reinoName}".`;
                }
            } else {
                responseText = "Guardián: Comando inválido. Usa: entrar en templo [nombre] de [reino].";
            }

        // Comando: salir del templo
        } else if (lowerCaseCommand.trim() === 'salir del templo') {
            if (guardianData.activeContext.templo) {
                const temploAnterior = guardianData.activeContext.templo;
                guardianData.activeContext.reino = null;
                guardianData.activeContext.templo = null;
                responseText = `Guardián: Has salido del Templo "${temploAnterior}". Tu foco ha sido liberado.`;
            } else {
                responseText = `Guardián: No estás dentro de ningún Templo.`;
            }

        // Comando: estado
        } else if (lowerCaseCommand.trim() === 'estado') {
            const { reino, templo } = guardianData.activeContext;
            if (templo) {
                responseText = `Guardián: Tu foco actual es el Templo "${templo}" en el Reino de "${reino}".`;
            } else {
                responseText = `Guardián: No tienes un foco activo. Estás operando a nivel de Reinos.`;
            }

        // Comando: contrato de duración (legado, sin contexto)
        } else {
            const durationMatch = lowerCaseCommand.match(/(\d+)\s*(minutos|min|m)/);
            if (durationMatch) {
                const duration = parseInt(durationMatch[1], 10);
                const task = command.replace(durationMatch[0], '').trim();
                responseText = `Guardián: Contrato aceptado. Tarea: '${task}'. Duración: ${duration} minutos. El tiempo empieza ahora.`;
            } else {
                responseText = "Guardián: Comando no reconocido. Revisa los comandos disponibles o define un contrato con duración.";
            }
        }
        
        // Añadir respuesta del Guardián y guardar datos
        addMessage(responseText, 'guardian-message');
        guardianData.chat_history.push({ text: responseText, sender: 'guardian-message' });
        saveData();
    }

    // --- PUNTO DE ENTRADA ---
    loadData();
}
