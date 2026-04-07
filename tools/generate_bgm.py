import wave, struct, math
import os

print("Generando bgm.wav...")
sample_rate = 44100
duration = 16.0 
freq1 = 65.41 # C2
freq2 = 66.0 # Drone detune
freq3 = 98.00 # G2

wavef = wave.open('bgm.wav','w')
wavef.setnchannels(1) 
wavef.setsampwidth(2) 
wavef.setframerate(sample_rate)

for i in range(int(sample_rate * duration)):
    t = float(i) / sample_rate
    # Oscilacion suave para darle sensacion de viento/respiracion
    lfo = (math.sin(2.0 * math.pi * 0.2 * t) + 1) / 2.0 
    
    val1 = math.sin(2.0 * math.pi * freq1 * t)
    val2 = math.sin(2.0 * math.pi * freq2 * t)
    val3 = math.sin(2.0 * math.pi * freq3 * t) * lfo
    
    value = int( 6000 * val1 + 6000 * val2 + 4000 * val3 )
    
    # Clip by boundary
    if value > 32767: value = 32767
    elif value < -32768: value = -32768
    
    data = struct.pack('<h', value)
    wavef.writeframesraw(data)

wavef.close()
print("Terminado.")
