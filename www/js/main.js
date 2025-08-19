document.addEventListener('deviceready', onDeviceReady, false);

function onDeviceReady() {
    console.log('Dispositivo listo. Guardián operativo.');

    const chatBox = document.getElementById('chat-box');
    const userInput = document.getElementById('user-input');
    const sendButton = document.getElementById('send-button');

    // --- BASE DE DATOS EVOLUCIONADA ---
    let guardianData = {
        chat_history: [],
        reinos: [],
        activeContext: {
            reino: null,
            templo: null
        }
    };

    // --- LÓGICA DE ALMACENAMIENTO ---
    function loadData() {
        window.NativeStorage.getItem('guardian_data', (data) => {
            if (data) {
                guardianData = data;
                // Verificaciones de seguridad para evitar errores tras una actualización
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

        const userMessageText = `Tú: ${userText}`;
        addMessage(userMessageText, 'user-message');
        guardianData.chat_history.push({ text: userMessageText, sender: 'user-message' });
        
        processCommand(userText);

        userInput.value = "";
    }

    function addMessage(message, senderClass) {
        const messageElement = document.createElement('div');
        messageElement.className = `chat-message ${senderClass}`;
        messageElement.innerText = message;
        chatBox.appendChild(messageElement);
        chatBox.scrollTop = chatBox.scrollHeight;
    }

    // --- PROCESADOR DE COMANDOS (EL CEREBRO DEL GUARDIÁN) ---
    function processCommand(command) {
        let responseText = "";
        const lowerCaseCommand = command.toLowerCase();
        const { reino: activeReino, templo: activeTemplo } = guardianData.activeContext;

        // --- LÓGICA DE COMANDOS GLOBALES ---

        // Comando: crear reino [nombre]
        if (lowerCaseCommand.startsWith('crear reino ')) {
            const reinoName = command.substring(12).trim();
            const reinoExists = guardianData.reinos.some(r => r.name.toLowerCase() === reinoName.toLowerCase());

            if (reinoName && !reinoExists) {
                const nuevoReino = { name: reinoName, templos: [] };
                guardianData.reinos.push(nuevoReino);
                responseText = `Guardián: Reino "${reinoName}" creado con éxito. Tu universo se expande.`;
            } else if (reinoExists) {
                responseText = `Guardián: El Reino "${reinoName}" ya existe.`;
            } else {
                responseText = "Guardián: Comando inválido. Usa: crear reino [nombre].";
            }
        
        // Comando: listar reinos
        } else if (lowerCaseCommand.trim() === 'listar reinos') {
            if (guardianData.reinos.length > 0) {
                const reinoNames = guardianData.reinos.map(r => r.name);
                responseText = "Guardián: Tus Reinos actuales:\n- " + reinoNames.join('\n- ');
            } else {
                responseText = "Guardián: Aún no has creado ningún Reino.";
            }

        // Comando: crear templo [nombre] en [reino]
        } else if (lowerCaseCommand.startsWith('crear templo ')) {
            const match = command.match(/crear templo (.*) en (.*)/i);
            if (match) {
                const temploName = match[1].trim();
                const reinoName = match[2].trim();
                const reinoTarget = guardianData.reinos.find(r => r.name.toLowerCase() === reinoName.toLowerCase());

                if (reinoTarget) {
                    const temploExists = reinoTarget.templos.some(t => t.name.toLowerCase() === temploName.toLowerCase());
                    if (!temploExists) {
                        const nuevoTemplo = { name: temploName, level: 1, contracts: [] };
                        reinoTarget.templos.push(nuevoTemplo);
                        responseText = `Guardián: Templo "${temploName}" erigido en el Reino de "${reinoName}".`;
                    } else {
                        responseText = `Guardián: El Templo "${temploName}" ya existe en ese Reino.`;
                    }
                } else {
                    responseText = `Guardián: No se encontró el Reino "${reinoName}".`;
                }
            } else {
                responseText = "Guardián: Comando inválido. Usa: crear templo [nombre] en [reino].";
            }

        // Comando: listar templos en [reino]
        } else if (lowerCaseCommand.startsWith('listar templos en ')) {
            const reinoName = command.substring(18).trim();
            const reinoTarget = guardianData.reinos.find(r => r.name.toLowerCase() === reinoName.toLowerCase());

            if (reinoTarget) {
                if (reinoTarget.templos.length > 0) {
                    const temploNames = reinoTarget.templos.map(t => `${t.name} (Nivel ${t.level})`);
                    responseText = `Guardián: Templos en "${reinoName}":\n- ` + temploNames.join('\n- ');
                } else {
                    responseText = `Guardián: El Reino de "${reinoName}" no tiene Templos.`;
                }
            } else {
                responseText = `Guardián: No se encontró el Reino "${reinoName}".`;
            }
            
        // Comando: entrar en templo [nombre] de [reino]
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
                        responseText = `Guardián: Foco establecido. Templo "${temploTarget.name}" del Reino "${reinoTarget.name}".`;
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
            if (activeTemplo) {
                const temploAnterior = activeTemplo;
                guardianData.activeContext.reino = null;
                guardianData.activeContext.templo = null;
                responseText = `Guardián: Has salido del Templo "${temploAnterior}". Foco liberado.`;
            } else {
                responseText = `Guardián: No estás dentro de ningún Templo.`;
            }

        // Comando: estado
        } else if (lowerCaseCommand.trim() === 'estado') {
            if (activeTemplo) {
                responseText = `Guardián: Foco actual: Templo "${activeTemplo}" (Reino: "${activeReino}").`;
            } else {
                responseText = `Guardián: Sin foco activo. Operando a nivel de Reinos.`;
            }
        
        // Comando: listar contratos en [templo] de [reino]
        } else if (lowerCaseCommand.startsWith('listar contratos en ')) {
            const match = command.match(/listar contratos en (.*) de (.*)/i);
             if (match) {
                const temploName = match[1].trim();
                const reinoName = match[2].trim();
                const reinoTarget = guardianData.reinos.find(r => r.name.toLowerCase() === reinoName.toLowerCase());

                if (reinoTarget) {
                    const temploTarget = reinoTarget.templos.find(t => t.name.toLowerCase() === temploName.toLowerCase());
                    if (temploTarget) {
                         if (temploTarget.contracts.length > 0) {
                            const contractDescriptions = temploTarget.contracts.map(c => `[${c.status}] ${c.description}`);
                            responseText = `Guardián: Contratos en Templo "${temploName}":\n- ` + contractDescriptions.join('\n- ');
                        } else {
                            responseText = `Guardián: El Templo "${temploName}" no tiene contratos.`;
                        }
                    } else {
                        responseText = `Guardián: No se encontró el Templo "${temploName}".`;
                    }
                } else {
                    responseText = `Guardián: No se encontró el Reino "${reinoName}".`;
                }
            } else {
                responseText = "Guardián: Comando inválido. Usa: listar contratos en [templo] de [reino].";
            }

        // --- LÓGICA CONTEXTUAL DE CONTRATOS ---
        // Si hay un templo activo, cualquier otra cosa es un contrato.
        } else if (activeTemplo) {
            const reino = guardianData.reinos.find(r => r.name === activeReino);
            const templo = reino.templos.find(t => t.name === activeTemplo);
            
            const nuevoContrato = {
                description: command,
                status: 'pendiente'
            };
            
            templo.contracts.push(nuevoContrato);
            responseText = `Guardián: Contrato añadido al Templo "${activeTemplo}":\n> ${command}`;

        // Si no hay templo activo y no es un comando conocido, es un error.
        } else {
            responseText = "Guardián: Comando no reconocido o acción inválida. Establece un foco con 'entrar en templo...' o usa un comando global.";
        }
        
        // Añadir respuesta del Guardián y guardar datos
        addMessage(responseText, 'guardian-message');
        guardianData.chat_history.push({ text: responseText, sender: 'guardian-message' });
        saveData();
    }

    // --- PUNTO DE ENTRADA ---
    loadData();
}
