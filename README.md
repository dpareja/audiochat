# AudioChat 🎧

Sistema de chat en tiempo real usando audio ultrasónico. Todos los participantes escuchan todos los mensajes (broadcast).

## Características

- 💬 **Chat en tiempo real**: Envía y recibe mensajes instantáneamente
- 🔇 **Ultrasónico**: Usa frecuencias 17-20.4 kHz (casi silencioso)
- 📡 **Broadcast**: Todos escuchan todos los mensajes
- 👥 **Multi-usuario**: Múltiples personas pueden chatear simultáneamente
- 🏷️ **Nombres de usuario**: Cada mensaje muestra quién lo envió
- ⏰ **Timestamps**: Hora de cada mensaje
- 🎯 **Simple**: Sin servidor, sin red, solo audio

## Requisitos

```bash
pip3 install numpy pyaudio
```

### Linux
```bash
sudo apt-get install portaudio19-dev python3-pyaudio
pip3 install numpy pyaudio
```

## Uso

Cada participante ejecuta:

```bash
python3 audio_chat.py TuNombre
```

Ejemplo con 3 usuarios:

**Terminal 1:**
```bash
$ python3 audio_chat.py Alice
🎧 AudioChat inicializado
   Usuario: Alice
   Frecuencias: 17000-20395 Hz

💬 Chat iniciado. Escribe tus mensajes:
   (Ctrl+C para salir)

> Hola a todos!
[18:30:15] Bob: Hola Alice!
[18:30:20] Charlie: Hey!
> ¿Cómo están?
```

**Terminal 2:**
```bash
$ python3 audio_chat.py Bob
> 
[18:30:10] Alice: Hola a todos!
> Hola Alice!
[18:30:20] Charlie: Hey!
[18:30:25] Alice: ¿Cómo están?
> Bien, gracias
```

**Terminal 3:**
```bash
$ python3 audio_chat.py Charlie
>
[18:30:10] Alice: Hola a todos!
[18:30:15] Bob: Hola Alice!
> Hey!
[18:30:25] Alice: ¿Cómo están?
[18:30:30] Bob: Bien, gracias
```

## Cómo Funciona

1. **Escucha continua**: Cada usuario escucha constantemente por mensajes
2. **Broadcast**: Cuando alguien escribe, todos lo escuchan
3. **Identificación**: Cada mensaje incluye el nombre del remitente
4. **Ultrasónico**: Usa frecuencias inaudibles (17-20.4 kHz)
5. **Sin servidor**: Comunicación directa por audio

## Formato de Mensaje

```
[Preámbulo: 0,7,0,7] [Longitud_nombre] [Nombre] [Mensaje]
```

- Preámbulo: Sincronización (4 símbolos)
- Longitud_nombre: 1 byte
- Nombre: Hasta 16 caracteres
- Mensaje: Hasta 64 caracteres

## Limitaciones

⚠ **Half-duplex**: Solo una persona puede hablar a la vez
⚠ **Colisiones**: Si dos personas escriben simultáneamente, puede haber interferencia
⚠ **Alcance**: Limitado por alcance de altavoces/micrófonos
⚠ **Sin privacidad**: Todos escuchan todo (broadcast público)
⚠ **Latencia**: ~100-200ms por mensaje

## Casos de Uso

- **Sala de reuniones**: Chat silencioso entre computadores cercanos
- **Clase**: Comunicación entre estudiantes sin cables
- **Oficina**: Chat entre escritorios sin red
- **Emergencias**: Comunicación cuando la red no funciona
- **Experimentos**: Demostración de comunicación por audio

## Ventajas

✓ **Sin red**: No requiere WiFi, Bluetooth ni cables
✓ **Silencioso**: Casi inaudible (frecuencias ultrasónicas)
✓ **Simple**: Sin configuración, sin servidor
✓ **Multiplataforma**: Funciona en cualquier OS con Python
✓ **Broadcast natural**: Todos escuchan automáticamente

## Comparación con Otros Chats

| Característica | AudioChat | WhatsApp/Telegram | IRC/Discord |
|----------------|-----------|-------------------|-------------|
| Requiere red | No | Sí | Sí |
| Requiere servidor | No | Sí | Sí |
| Privacidad | Pública (broadcast) | Privada | Configurable |
| Alcance | Local (audio) | Global | Global |
| Latencia | ~100ms | ~50-500ms | ~50-200ms |
| Instalación | Mínima | App completa | App/Cliente |

## Mejoras Futuras

- [ ] Cifrado de mensajes
- [ ] Salas privadas (diferentes frecuencias)
- [ ] Detección de colisiones
- [ ] Historial de mensajes
- [ ] Interfaz gráfica
- [ ] Emojis y formato
- [ ] Archivos adjuntos
- [ ] Mensajes privados (dirigidos)

## Troubleshooting

**No escucho mensajes:**
- Verifica que el volumen esté alto
- Asegúrate de que el micrófono esté activo
- Prueba con `test_ultrasonic_simple.py` del proyecto audioprotocol

**Mensajes cortados:**
- Reduce la distancia entre computadores
- Aumenta el volumen
- Verifica que no haya ruido ultrasónico (ventiladores, etc.)

**Colisiones frecuentes:**
- Espera a que termine el mensaje anterior
- Implementa un protocolo de turnos manual

## Licencia

MIT

## Créditos

Basado en AudioProtocol: https://github.com/dpareja/audioprotocol
