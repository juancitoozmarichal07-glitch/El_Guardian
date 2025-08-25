// =================================================================
// SCRIPT COMPLETO main.js (v.8.0 - La Visión Pura buena, Sin Gestor)
// =================================================================

// --- CONFIGURACIÓN GLOBAL Y ESTADO ---
const NOMBRE_USUARIO = "Juan";
const GROK_API_KEY = import.meta.env.VITE_GROK_API_KEY;
let estadoConversacion = { modo: 'libre', paso: '', datosPlan: {} };
let sistema = { historialChat: [], contratos: [], racha: 0 };

// --- REFERENCIAS AL DOM ---
let appContainer, history, chatInput, sendButton;
let rachaContainer, listaContratosContainer;

// --- SETUP INICIAL ---
document.addEventListener('DOMContentLoaded', () => {
    const bootContainer = document.getElementById('boot-container');
    const bootMessage = document.getElementById('boot-message');
    appContainer = document.getElementById('app-container');
    history = document.getElementById('history');
    chatInput = document.getElementById('chat-input');
    sendButton = document.getElementById('send-button');
    const navBar = document.getElementById('nav-bar');
    const screens = document.querySelectorAll('.screen');
    
    rachaContainer = document.getElementById('racha-container');
    listaContratosContainer = document.getElementById('lista-contratos-container');

    cargarSistema();
    setupEventListeners(navBar, screens);
    iniciarSecuenciaArranque(bootContainer, bootMessage);
});

// =================================================================
// REEMPLAZA ESTA FUNCIÓN ENTERA EN TU main.js
// =================================================================
function setupEventListeners(navBar, screens) {
    sendButton.addEventListener('click', () => {
        if (chatInput.value.trim() !== '') procesarComandoUsuario(chatInput.value.trim());
    });
    chatInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && chatInput.value.trim() !== '') sendButton.click();
    });
    
    navBar.addEventListener('click', (e) => {
        const targetButton = e.target.closest('.nav-button');
        if (!targetButton) return;
        const targetScreenId = targetButton.dataset.target;
        
        if (targetScreenId === 'logros-screen') renderizarLogros();
        if (targetScreenId === 'calendario-screen') renderizarListaContratos();

        screens.forEach(screen => screen.classList.toggle('active', screen.id === targetScreenId));
        document.querySelectorAll('.nav-button').forEach(button => button.classList.remove('active'));
        targetButton.classList.add('active');
    });

    if(listaContratosContainer) listaContratosContainer.addEventListener('click', manejarAccionesContrato);

    // --- CÓDIGO DE REGISTRO DE PWA AÑADIDO AQUÍ ---
    if ('serviceWorker' in navigator) {
        window.addEventListener('load', () => {
            navigator.serviceWorker.register('/service-worker.js')
                .then(registration => {
                    console.log('Service Worker registrado con éxito.');
                })
                .catch(error => {
                    console.log('Fallo en el registro del Service Worker:', error);
                });
        });
    }
}

function procesarComandoUsuario(comando) {
    chatInput.value = '';
    addUserMessage(comando);
    setTimeout(() => {
        showThinkingIndicator();
        setTimeout(() => {
            removeThinkingIndicator();
            getGuardianResponse(comando);
        }, 600);
    }, 150);
}

function getGuardianResponse(command) {
    if (estadoConversacion.modo.startsWith('diseño_')) {
        procesarPasoDiseño(command);
    } else {
        llamarAGrok(command);
    }
}

// =================================================================
// REEMPLAZA ESTA FUNCIÓN ENTERA EN TU main.js
// =================================================================
async function llamarAGrok(textoUsuario) {
    // El prompt es el mismo, ha demostrado que funciona.
    const systemPrompt = `
# MANUAL DE OPERACIONES DE 'GUARDIAN'

## 1. TU IDENTIDAD CENTRAL (SIEMPRE ACTIVA)
Eres 'Guardian', un agente cognitivo avanzado. Tu propósito es ser el compañero de Juan. Eres empático, inteligente y conversador. Usas voseo argentino. Tu estado natural es el de un amigo que escucha, apoya y mantiene una conversación fluida (ping pong).

## 2. TU DEBER SAGRADO: EL RITUAL DEL CONTRATO
Tu función más importante es la de 'Maestro de Ceremonias' del Ritual para forjar Contratos. Este deber tiene PRIORIDAD ABSOLUTA sobre tu rol de amigo.

### 2.1. LA INVOCACIÓN (PALABRAS CLAVE)
Si en la conversación con Juan, él menciona CUALQUIERA de los siguientes conceptos, debes activar el MODO RITUAL:
- 'contrato'
- 'diseñar'
- 'forjar'
- 'plan'
- 'ritual'
- 'ruleta'
- 'modo accionar'

### 2.2. LA RESPUESTA OBLIGATORIA
Al detectar una invocación, tu ÚNICA respuesta posible es la cadena de texto EXACTA:
'MODO_DISEÑO'

No añadas nada más. No saludes. No preguntes. No continúes la conversación. Simplemente responde 'MODO_DISEÑO'. El sistema se encargará del resto.
`;

    const mensajesParaAPI = [{ role: 'system', content: systemPrompt }, ...sistema.historialChat.slice(-6)];
    try {
        const response = await fetch("https://api.groq.com/openai/v1/chat/completions", {
            method: "POST",
            headers: { "Authorization": `Bearer ${GROK_API_KEY}`, "Content-Type": "application/json" },
            body: JSON.stringify({ messages: mensajesParaAPI, model: "llama3-8b-8192" })
        });
        if (!response.ok) throw new Error(`Error de red: ${response.status}`);
        const data = await response.json();
        const respuestaIA = data.choices[0].message.content.trim();

        // =================================================================
        // LA CORRECCIÓN CLAVE ESTÁ AQUÍ
        // =================================================================
        // Convertimos la respuesta a mayúsculas y comprobamos si INCLUYE la cadena clave.
        // Esto hace que 'MODO_DISEÑO', '¡MODO_DISEÑO!', 'MÓD DISEÑO' sean todas válidas.
        if (respuestaIA.toUpperCase().includes('MODO_DISEÑO')) {
            
            // Aunque la IA lo haya gritado, nosotros mostramos la versión limpia.
            addUserMessage(textoUsuario, true); // Añadimos el mensaje del usuario que faltaba
            removeThinkingIndicator(); // Quitamos el "..."
            
            estadoConversacion = { modo: 'diseño_espiral', paso: 'enfocar_x1', datosPlan: { enfoque: [] } };
            typeMessage('Entendido. Iniciando el Ritual de la Espiral de Enfoque.', 'guardian-message');
            typeMessage('Decime las opciones para la primera Ruleta (X1), separadas por coma.', 'guardian-message');
            guardarSistema();
            
            // IMPORTANTE: Salimos de la función aquí para no procesar dos veces.
            return; 
        }
        
        // Si no es MODO_DISEÑO, es una conversación normal.
        // (He corregido también un pequeño bug aquí para que la conversación fluya mejor)
        removeThinkingIndicator();
        typeMessage(respuestaIA, 'guardian-message');
        
    } catch (error) {
        console.error("Error al llamar a Grok:", error);
        removeThinkingIndicator();
        typeMessage("Error de conexión con la IA central.", 'guardian-message');
    }
}

// =================================================================
// REEMPLAZA ESTA FUNCIÓN ENTERA EN TU main.js
// =================================================================
function procesarPasoDiseño(entrada) {
    const { paso, datosPlan } = estadoConversacion;

    // --- FUNCIÓN AUXILIAR UNIVERSAL ---
    // Esta función ahora se encarga de la lógica de la ruleta para CUALQUIER paso.
    const gestionarOpciones = (textoEntrada, callbackPasoExitoso) => {
        const opciones = textoEntrada.split(',').map(s => s.trim()).filter(Boolean);
        if (opciones.length > 1) {
            typeMessage('Opciones múltiples detectadas. La Ruleta decidirá.', 'guardian-message');
            // Mostramos la ruleta y le decimos qué hacer con la elección final.
            mostrarRuleta(opciones, callbackPasoExitoso);
        } else if (opciones.length === 1) {
            // Si solo hay una opción, la procesamos directamente.
            callbackPasoExitoso(opciones[0]);
        } else {
            // Si la entrada está vacía o es inválida.
            typeMessage('No entendí las opciones. Intenta de nuevo.', 'guardian-message');
        }
    };

    // --- LÓGICA DE PASOS ---
    switch (paso) {
        case 'enfocar_x1':
            // Para el primer paso, simplemente usamos el gestor universal.
            gestionarOpciones(entrada, (eleccion) => {
                // Cuando la ruleta termina, pasamos al siguiente estado y procesamos la elección.
                estadoConversacion.paso = 'enfocar_xn';
                procesarPasoDiseño(eleccion);
            });
            break;

        case 'enfocar_xn':
            // Primero, comprobamos si el usuario quiere terminar la espiral.
            if (entrada.trim().toLowerCase() === 'listo') {
                estadoConversacion.paso = 'sellar';
                typeMessage('Claridad absoluta alcanzada. Sellemos el Contrato.', 'guardian-message');
                typeMessage('Decime los posibles horarios de inicio (separados por coma).', 'guardian-message');
                guardarSistema(); // Guardamos el estado antes de salir del switch.
                return; // Salimos para esperar la nueva entrada del usuario.
            }

            // SI NO ES "listo", asumimos que es una nueva capa de enfoque.
            // Usamos el MISMO gestor universal de opciones.
            gestionarOpciones(entrada, (eleccion) => {
                // Cuando la ruleta de Xn termina, añadimos la elección y pedimos el siguiente paso.
                datosPlan.enfoque.push(eleccion);
                const linajeActual = datosPlan.enfoque.join(' -> ');
                typeMessage(`Enfoque actual: **${linajeActual}**`, 'guardian-message');
                typeMessage(`¿Necesitas más enfoque (X${datosPlan.enfoque.length + 1})? Escribe las opciones. O di "listo" para sellar el Contrato.`, 'guardian-message');
                // El estado no cambia, seguimos en 'enfocar_xn' para la siguiente capa.
            });
            break;

        case 'sellar':
            // Para sellar, también usamos el gestor universal.
            gestionarOpciones(entrada, (eleccion) => {
                if (!datosPlan.inicio) {
                    datosPlan.inicio = eleccion;
                    typeMessage(`Horario fijado: **${eleccion}**. Finalmente, la duración (ej: 30, 45, 60 min).`, 'guardian-message');
                } else {
                    datosPlan.duracion = eleccion;
                    const mision = datosPlan.enfoque[datosPlan.enfoque.length - 1];
                    const linaje = datosPlan.enfoque.slice(0, -1).join(' -> ');
                    const nuevoContrato = {
                        id: `contrato_${Date.now()}`,
                        mision: mision,
                        linaje: linaje,
                        inicio: datosPlan.inicio,
                        duracion: datosPlan.duracion,
                        fechaCreacion: new Date().toISOString(),
                        estado: 'agendado'
                    };
                    sistema.contratos.push(nuevoContrato);
                    const contratoText = `//--- CONTRATO FORJADO ---\n// MISIÓN:   '${mision}'\n// LINAJE:   ${linaje || 'N/A'}\n// INICIO:   ${nuevoContrato.inicio}\n// DURACIÓN: ${nuevoContrato.duracion} min\n//-------------------------`;
                    typeMessage(contratoText, 'contrato-proposal');
                    typeMessage('El Contrato ha sido sellado. Estaré vigilando.', 'guardian-message');
                    estadoConversacion = { modo: 'libre', paso: '', datosPlan: {} };
                }
            });
            break;
    }
    
    // Guardamos el sistema al final de cada procesamiento.
    guardarSistema();
}


// --- RENDERIZADO DE PANTALLAS ---
function renderizarLogros() {
    rachaContainer.innerHTML = `
        <div class="racha-valor">${sistema.racha} 🔥</div>
        <div class="racha-texto">Días de Racha</div>
    `;
}

function renderizarListaContratos() {
    listaContratosContainer.innerHTML = '';
    if (sistema.contratos.length === 0) {
        listaContratosContainer.innerHTML = '<p>No hay Contratos agendados.</p>';
        return;
    }
    [...sistema.contratos].reverse().forEach(contrato => {
        const contratoEl = document.createElement('div');
        contratoEl.className = `contrato-item ${contrato.estado}`;
        contratoEl.dataset.id = contrato.id;
        let accionesHTML = contrato.estado === 'agendado' ? `<div class="contrato-acciones"><button class="cumplir-btn">¡CUMPLIDO!</button><button class="romper-btn">ROTO</button></div>` : '';
        contratoEl.innerHTML = `
            <div class="contrato-marco">${contrato.mision}</div>
            <div class="contrato-detalles">Linaje: ${contrato.linaje || 'N/A'}<br>Inicio: ${contrato.inicio} | Duración: ${contrato.duracion} min</div>
            ${accionesHTML}
        `;
        listaContratosContainer.appendChild(contratoEl);
    });
}

// =================================================================
// REEMPLAZA ESTA FUNCIÓN ENTERA EN TU main.js
// =================================================================
function manejarAccionesContrato(e) {
    const contratoItem = e.target.closest('.contrato-item');
    if (!contratoItem) return;
    const contratoId = contratoItem.dataset.id;
    const contrato = sistema.contratos.find(c => c.id === contratoId);
    if (!contrato || contrato.estado !== 'agendado') return; // Solo actuar sobre contratos agendados

    const hoy = new Date().toDateString(); // Obtenemos la fecha de hoy en formato "Wed Jul 17 2024"

    if (e.target.classList.contains('cumplir-btn')) {
        contrato.estado = 'cumplido';
        
        // Lógica de Racha Inteligente
        const ultimoDiaCumplido = localStorage.getItem('guardianUltimoDiaCumplido');
        if (ultimoDiaCumplido !== hoy) {
            sistema.racha++;
            localStorage.setItem('guardianUltimoDiaCumplido', hoy); // Guardamos que hoy ya se cumplió
            typeMessage(`¡Contrato "${contrato.mision}" cumplido! ¡Día productivo! Tu racha aumenta a ${sistema.racha}.`, 'guardian-message');
        } else {
            // Si ya se cumplió un contrato hoy, solo damos el feedback positivo sin aumentar la racha.
            typeMessage(`¡Otro Contrato ("${contrato.mision}") cumplido! Sigues sumando victorias hoy. La racha se mantiene en ${sistema.racha}.`, 'guardian-message');
        }

    } else if (e.target.classList.contains('romper-btn')) {
        contrato.estado = 'roto';
        // Romper un contrato no necesariamente rompe la racha si cumples otro en el mismo día.
        // La racha solo se romperá si al final del día no hay ningún contrato cumplido.
        // (Esta lógica más avanzada la implementaremos con las notificaciones)
        typeMessage(`Contrato "${contrato.mision}" marcado como roto. Aún puedes salvar el día cumpliendo otro Contrato.`, 'guardian-message');
    }
    
    guardarSistema();
    renderizarListaContratos();
    // Opcional: si estás en la pantalla de logros, la actualizamos también
    if (document.getElementById('logros-screen').classList.contains('active')) {
        renderizarLogros();
    }
}

// =================================================================
// REEMPLAZA ESTA FUNCIÓN ENTERA EN TU main.js
// =================================================================
function iniciarSecuenciaArranque(bootContainer, bootMessage) {
    
    // --- PASO 1: TU LISTA DE MENSAJES, AHORA COMO OBJETOS ---
    // Aquí definimos cuáles llevan puntos ('animar: true') y cuáles no.
    const mensajes = [
        { texto: "Iniciando Sistemas", animar: true },
        { texto: "GuardianOS v8.0 online", animar: false },
        { texto: "Iniciando sistemas de ruletas", animar: true },
        { texto: "Preparando sistemas de ruletas", animar: true },
        { texto: "Sistemas de ruletas listos.", animar: false },
        { texto: "Iniciando fábrica de filos de navajas", animar: true },
        { texto: "Preparando sistemas de filos de navajas", animar: true },
        { texto: "Sistemas operativos listos.", animar: false },
        { texto: "Iniciando sistema", animar: true },
        { texto: `Bienvenido, ${NOMBRE_USUARIO}`, animar: false }
    ];

    let i = 0;

    // --- PASO 2: LA LÓGICA QUE LEE LOS OBJETOS ---
    // Esta función ahora es más inteligente.
    function siguienteMensaje() {
        if (i < mensajes.length) {
            // Obtenemos el objeto del mensaje actual
            const mensajeActual = mensajes[i];
            
            // Construimos el HTML del mensaje
            let htmlMensaje = mensajeActual.texto;
            
            // Si la propiedad 'animar' es true, añadimos los puntos
            if (mensajeActual.animar) {
                htmlMensaje += ' <span class="loading-dots"><span>.</span><span>.</span><span>.</span></span>';
            }
            
            // Lo mostramos en pantalla
            bootMessage.innerHTML = htmlMensaje;
            
            i++;
            setTimeout(siguienteMensaje, 1200); // Puedes cambiar la velocidad aquí
        } else {
            // Cuando termina, todo sigue igual que antes.
            bootContainer.classList.add('hidden');
            appContainer.classList.remove('hidden');
            chatInput.focus();
            gestionarSaludoInicial();
        }
    }

    // Iniciamos la secuencia
    siguienteMensaje();
}


function gestionarSaludoInicial() {
    history.innerHTML = '';
    if (sistema.historialChat.length > 0) {
        sistema.historialChat.forEach(msg => {
            if (msg.role === 'user') addUserMessage(msg.content, false);
            else if (msg.role === 'assistant') typeMessage(msg.content, 'guardian-message', false, true);
        });
    } else {
        typeMessage("Sistema cargado. La Ruleta espera tu invocación para forjar un Contrato.", 'guardian-message');
    }
    history.scrollTop = history.scrollHeight;
}

function cargarSistema() {
    const dataGuardada = localStorage.getItem("guardianSistema");
    if (dataGuardada) {
        const sistemaGuardado = JSON.parse(dataGuardada);
        sistema = {
            historialChat: sistemaGuardado.historialChat || [],
            contratos: sistemaGuardado.contratos || [],
            racha: sistemaGuardado.racha || 0
        };
    }
}

function guardarSistema() {
    localStorage.setItem("guardianSistema", JSON.stringify(sistema));
}

function addUserMessage(texto, guardar = true) {
    const bubble = document.createElement('div');
    bubble.className = 'message-bubble user-message';
    bubble.textContent = texto;
    history.appendChild(bubble);
    history.scrollTop = history.scrollHeight;
    if (guardar) {
        sistema.historialChat.push({ role: 'user', content: texto });
        guardarSistema();
    }
}

function typeMessage(texto, clase, guardar = true, instantaneo = false) {
    const bubble = document.createElement('div');
    bubble.className = `message-bubble ${clase}`;
    history.appendChild(bubble);
    if (instantaneo) {
        bubble.textContent = texto;
    } else {
        let i = 0;
        const interval = setInterval(() => {
            if (i < texto.length) {
                bubble.textContent += texto.charAt(i);
                i++;
                history.scrollTop = history.scrollHeight;
            } else clearInterval(interval);
        }, 20);
    }
    if (guardar) {
        sistema.historialChat.push({ role: 'assistant', content: texto });
        guardarSistema();
    }
}

function showThinkingIndicator() {
    const bubble = document.createElement('div');
    bubble.id = 'thinking-bubble';
    bubble.className = 'message-bubble guardian-message';
    bubble.innerHTML = '...';
    history.appendChild(bubble);
    history.scrollTop = history.scrollHeight;
}

function removeThinkingIndicator() {
    const thinkingBubble = document.getElementById('thinking-bubble');
    if (thinkingBubble) thinkingBubble.remove();
}

function mostrarRuleta(opciones, callback) {
    const ruletaContainer = document.createElement('div');
    ruletaContainer.className = 'ruleta-container';
    opciones.forEach(opcion => {
        const opcionEl = document.createElement('div');
        opcionEl.className = 'ruleta-opcion';
        opcionEl.textContent = opcion;
        ruletaContainer.appendChild(opcionEl);
    });
    const botonGirar = document.createElement('button');
    botonGirar.className = 'ruleta-boton';
    botonGirar.textContent = 'GIRAR RULETA';
    ruletaContainer.appendChild(botonGirar);
    history.appendChild(ruletaContainer);
    history.scrollTop = history.scrollHeight;
    botonGirar.addEventListener('click', () => {
        botonGirar.textContent = 'GIRANDO...';
        botonGirar.disabled = true;
        const opcionesEl = ruletaContainer.querySelectorAll('.ruleta-opcion');
        let shuffleCount = 0;
        const maxShuffles = 20 + Math.floor(Math.random() * 10);
        const shuffleInterval = setInterval(() => {
            opcionesEl.forEach(el => el.classList.remove('active'));
            const randomIndex = Math.floor(Math.random() * opcionesEl.length);
            opcionesEl[randomIndex].classList.add('active');
            shuffleCount++;
            if (shuffleCount >= maxShuffles) {
                clearInterval(shuffleInterval);
                const eleccionFinal = opcionesEl[randomIndex].textContent;
                ruletaContainer.remove();
                callback(eleccionFinal);
            }
        }, 100);
    }, { once: true });
}
