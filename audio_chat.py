#!/usr/bin/env python3
import sys
import pyaudio
import numpy as np
import threading
import time
from datetime import datetime

class AudioChat:
    def __init__(self, username):
        self.username = username[:16]  # Máximo 16 caracteres
        self.sample_rate = 44100
        self.bit_duration = 0.004  # 4ms por símbolo
        self.samples_per_bit = int(self.sample_rate * self.bit_duration)
        
        # 8 frecuencias ultrasónicas (17-20.4 kHz)
        self.freqs = {}
        base_freq = 17000
        for i in range(8):
            self.freqs[i] = base_freq + (i * 485)
        
        self.audio = pyaudio.PyAudio()
        self.stream_in = None
        self.stream_out = None
        self.buffer = np.array([], dtype=np.float32)
        self.running = False
        
        print(f"🎧 AudioChat inicializado")
        print(f"   Usuario: {self.username}")
        print(f"   Frecuencias: {self.freqs[0]}-{self.freqs[7]} Hz")
    
    def start(self):
        """Inicia el chat (escucha y envío)"""
        self.running = True
        
        # Stream de entrada (escucha)
        self.stream_in = self.audio.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=self.sample_rate,
            input=True,
            frames_per_buffer=self.samples_per_bit * 4
        )
        
        # Stream de salida (envío)
        self.stream_out = self.audio.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=self.sample_rate,
            output=True
        )
        
        # Thread para escuchar
        listen_thread = threading.Thread(target=self._listen_loop, daemon=True)
        listen_thread.start()
        
        # Thread para enviar
        self._send_loop()
    
    def _listen_loop(self):
        """Loop de escucha continua"""
        while self.running:
            try:
                # Leer audio
                data = self.stream_in.read(self.samples_per_bit * 4, exception_on_overflow=False)
                audio_chunk = np.frombuffer(data, dtype=np.int16).astype(np.float32) / 32767.0
                
                # Agregar al buffer
                self.buffer = np.append(self.buffer, audio_chunk)
                
                # Procesar buffer
                if len(self.buffer) >= self.samples_per_bit * 20:
                    self._process_buffer()
                    
                    # Limpiar buffer viejo
                    if len(self.buffer) > self.samples_per_bit * 100:
                        self.buffer = self.buffer[-self.samples_per_bit * 50:]
            
            except Exception as e:
                pass
    
    def _process_buffer(self):
        """Procesa buffer buscando mensajes"""
        # Buscar preámbulo [0, 7, 0, 7]
        if len(self.buffer) < self.samples_per_bit * 30:
            return
        
        # Decodificar símbolos
        symbols = []
        for i in range(0, min(len(self.buffer), self.samples_per_bit * 50), self.samples_per_bit):
            chunk = self.buffer[i:i+self.samples_per_bit]
            if len(chunk) < self.samples_per_bit:
                break
            symbols.append(self._detect_symbol(chunk))
        
        # Buscar patrón de preámbulo
        for i in range(len(symbols) - 4):
            if symbols[i:i+4] == [0, 7, 0, 7]:
                # Encontrado preámbulo
                message_symbols = symbols[i+4:i+50]  # Máximo 50 símbolos
                message = self._decode_message(message_symbols)
                
                if message:
                    sender, text = message
                    if sender != self.username:  # No mostrar propios mensajes
                        timestamp = datetime.now().strftime("%H:%M:%S")
                        print(f"\r[{timestamp}] {sender}: {text}")
                        print(f"> ", end="", flush=True)
                
                # Limpiar buffer
                self.buffer = self.buffer[(i+50)*self.samples_per_bit:]
                return
    
    def _detect_symbol(self, chunk):
        """Detecta símbolo usando Goertzel"""
        max_energy = 0
        detected_symbol = 0
        
        for symbol, target_freq in self.freqs.items():
            k = int(0.5 + (len(chunk) * target_freq) / self.sample_rate)
            omega = (2.0 * np.pi * k) / len(chunk)
            coeff = 2.0 * np.cos(omega)
            
            q0 = 0.0
            q1 = 0.0
            q2 = 0.0
            
            for sample in chunk:
                q0 = coeff * q1 - q2 + sample
                q2 = q1
                q1 = q0
            
            real = q1 - q2 * np.cos(omega)
            imag = q2 * np.sin(omega)
            energy = real * real + imag * imag
            
            if energy > max_energy:
                max_energy = energy
                detected_symbol = symbol
        
        return detected_symbol
    
    def _decode_message(self, symbols):
        """Decodifica mensaje desde símbolos"""
        # Convertir a bits
        bits = []
        for symbol in symbols:
            for i in range(2, -1, -1):
                bits.append((symbol >> i) & 1)
        
        # Convertir a bytes
        data = bytearray()
        for i in range(0, len(bits), 8):
            if i + 8 <= len(bits):
                byte = 0
                for j in range(8):
                    byte = (byte << 1) | bits[i+j]
                data.append(byte)
        
        if len(data) < 2:
            return None
        
        # Formato: [username_len(1B)][username][message]
        username_len = data[0]
        if len(data) < 1 + username_len:
            return None
        
        sender = data[1:1+username_len].decode('utf-8', errors='ignore')
        message = data[1+username_len:].decode('utf-8', errors='ignore').rstrip('\x00')
        
        return sender, message
    
    def _send_loop(self):
        """Loop para enviar mensajes"""
        print("\n💬 Chat iniciado. Escribe tus mensajes:")
        print("   (Ctrl+C para salir)\n")
        
        try:
            while self.running:
                message = input("> ")
                if message.strip():
                    self._send_message(message[:64])  # Máximo 64 caracteres
        except KeyboardInterrupt:
            print("\n\n✓ Chat cerrado")
            self.stop()
    
    def _send_message(self, message):
        """Envía un mensaje"""
        # Preparar datos: [username_len][username][message]
        username_bytes = self.username.encode('utf-8')
        message_bytes = message.encode('utf-8')
        
        data = bytearray()
        data.append(len(username_bytes))
        data.extend(username_bytes)
        data.extend(message_bytes)
        
        # Generar preámbulo
        audio = list(self._generate_preamble())
        
        # Convertir a bits
        bits = []
        for byte in data:
            for i in range(8):
                bits.append((byte >> (7-i)) & 1)
        
        # Convertir a símbolos (3 bits por símbolo)
        symbols = []
        for i in range(0, len(bits), 3):
            symbol = 0
            for j in range(3):
                if i+j < len(bits):
                    symbol = (symbol << 1) | bits[i+j]
                else:
                    symbol = symbol << 1
            symbols.append(symbol)
        
        # Generar audio
        for symbol in symbols:
            audio.extend(self._generate_tone(symbol))
        
        # Normalizar y enviar
        audio = np.array(audio)
        audio = (audio * 32767 * 0.9).astype(np.int16)
        
        self.stream_out.write(audio.tobytes())
    
    def _generate_preamble(self):
        """Genera preámbulo de sincronización"""
        preamble = []
        for symbol in [0, 7, 0, 7]:
            preamble.extend(self._generate_tone(symbol))
        return np.array(preamble)
    
    def _generate_tone(self, symbol):
        """Genera tono para un símbolo"""
        freq = self.freqs[symbol]
        t = np.linspace(0, self.bit_duration, self.samples_per_bit, False)
        return np.sin(2 * np.pi * freq * t)
    
    def stop(self):
        """Detiene el chat"""
        self.running = False
        if self.stream_in:
            self.stream_in.stop_stream()
            self.stream_in.close()
        if self.stream_out:
            self.stream_out.stop_stream()
            self.stream_out.close()
        self.audio.terminate()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Uso: python3 audio_chat.py <tu_nombre>")
        sys.exit(1)
    
    chat = AudioChat(sys.argv[1])
    try:
        chat.start()
    except KeyboardInterrupt:
        chat.stop()
