// Espera a que el dispositivo esté listo para usar las funciones de Cordova
document.addEventListener('deviceready', onDeviceReady, false);

function onDeviceReady() {
    // Elementos de la interfaz
    const commandInput = document.getElementById('command-input');
    const sendButton = document.getElementById('send-button');
    
    // Mensaje de bienvenida del Guardián
    addMessage("Guardián: Estoy listo. Define tu próximo contrato.", 'guardian-message');

    // Asignar eventos
    sendButton.addEventListener('click', handleSendCommand);
    commandInput.addEventListener('keypress', function(e) {
        // Permitir enviar con la tecla "Enter" del teclado
        if (e.key === 'Enter') {
            handleSendCommand();
        }
    });
}

function handleSendCommand() {
    const input = document.getElementById('command-input');
    const commandText = input.value.trim();

    // No hacer nada si el input está vacío
    if (commandText === '') return;

    // Mostrar el mensaje del usuario en el chat
    addMessage(`Tú: ${commandText}`, 'user-message');
    // Enviar el comando al intérprete
    interpretCommand(commandText);
    
    // Limpiar el campo de texto y mantener el foco
    input.value = '';
    input.focus();
}

function addMessage(text, type) {
    const container = document.getElementById('chat-container');
    const msgDiv = document.createElement('div');
    msgDiv.className = `message ${type}`;
    msgDiv.textContent = text;
    container.appendChild(msgDiv);
    
    // Pequeño truco para asegurar que el scroll baje después de que el DOM se actualice
    setTimeout(() => {
        container.scrollTop = container.scrollHeight;
    }, 0);
}

function interpretCommand(command) {
    const normalized = command.toLowerCase();
    // Expresión regular para encontrar números seguidos de "min", "minuto", "hora", etc.
    const durationRegex = /(\d+)\s*(min|minuto|minutos|hora|horas)/;
    const match = normalized.match(durationRegex);

    if (match) {
        // Si se encuentra una duración
        const value = parseInt(match[1], 10);
        const unit = match[2];
        // Convertir todo a minutos
        const duration = unit.startsWith('h') ? value * 60 : value;
        // La tarea es el resto del texto, limpiando la duración y espacios extra
        const task = normalized.replace(durationRegex, '').replace(/por$/, '').trim();
        
        const taskName = task.length > 0 ? `'${task}'` : 'una tarea';

        addMessage(`Guardián: Contrato aceptado. Tarea: ${taskName}. Duración: ${duration} minutos. El tiempo empieza ahora.`, 'guardian-message');
        // Futuro: Aquí iniciaremos el temporizador con un plugin nativo.
    } else {
        // Si no se encuentra una duración
        addMessage("Guardián: No he reconocido una duración. Ejemplo: 'Leer sobre IA por 30 minutos'.", 'guardian-message');
    }
}
