# Guia de Uso - AR Fluid Vision

## Início Rápido

### 1. Instalação Rápida

```bash
# Clone o repositório
git clone https://github.com/matheussiqueirahub/AR-Fluid-Vision-Real-Time-Augmented-Fluid-Dynamics-Simulation.git
cd AR-Fluid-Vision-Real-Time-Augmented-Fluid-Dynamics-Simulation

# Execute o script de setup (Linux/Mac)
./setup.sh

# Ou instale manualmente
python -m venv venv
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
```

### 2. Teste Rápido

Verifique se tudo está funcionando:

```bash
python test_system.py
```

### 3. Execute o Demo (Sem Câmera)

```bash
python demo.py
```

## Modos de Uso

### Modo 1: Demo Interativo (Sem Câmera)

O modo demo é ideal para testar o sistema sem necessidade de câmera ou marcadores AR.

```bash
python demo.py
```

**Características:**
- ✓ Não requer câmera
- ✓ Simulação de interação automatizada
- ✓ Visualização em tempo real
- ✓ Ideal para testes e demonstrações

**Controles:**
- `ESPAÇO` - Pausar/Retomar
- `A` - Ligar/Desligar movimento automático
- `R` - Resetar simulação
- `Q` ou `ESC` - Sair

### Modo 2: Aplicação AR Completa (Com Câmera)

A aplicação completa utiliza câmera para AR tracking e reconhecimento de gestos.

```bash
python main.py
```

**Requisitos:**
- Câmera/webcam conectada
- Marcador ArUco impresso (opcional, mas recomendado)
- Boa iluminação

**Controles:**
- `ESPAÇO` - Pausar/Retomar
- `R` - Resetar simulação
- `D` - Alternar debug info
- `Q` ou `ESC` - Sair

**Gestos Reconhecidos:**
- 👆 **Dedo indicador**: Empurra fluido
- 🖐️ **Mão aberta**: Atrai partículas
- ✊ **Punho fechado**: Repulsa forte
- ✌️ **Sinal de paz**: Força extra

### Modo 3: Exemplos Individuais

#### Simulação Básica (Sem AR)

```bash
cd examples
python basic_simulation.py
```

Mostra simulação 3D usando matplotlib (sem câmera ou AR).

#### Teste de Reconhecimento de Gestos

```bash
cd examples
python test_gesture_recognition.py
```

Testa apenas o sistema de reconhecimento de gestos.

#### Teste de Detecção ArUco

```bash
cd examples
python test_aruco_detection.py
```

Testa apenas a detecção de marcadores ArUco.

## Preparação para AR

### 1. Gerando Marcadores ArUco

Para melhor tracking AR, imprima um marcador ArUco:

1. Acesse: https://chev.me/arucogen/
2. Selecione: **Dictionary: 6x6 (250)**
3. Defina: **Marker ID: 0** (ou qualquer ID de 0-249)
4. Defina: **Marker size: 150mm** (ou maior)
5. Baixe e imprima o marcador

**Dicas:**
- Use papel branco de boa qualidade
- Imprima em alta resolução
- Cole em cartolina para maior rigidez
- Evite reflexos e dobras

### 2. Configuração da Câmera

Edite `config.py` para ajustar sua câmera:

```python
VISION_CONFIG = {
    'camera_id': 0,              # Mude se tiver múltiplas câmeras
    'resolution': (1280, 720),   # Ajuste conforme sua câmera
    'fps': 30,
}
```

### 3. Calibração (Opcional)

Para melhor precisão, calibre sua câmera usando ferramentas do OpenCV.

## Ajuste de Parâmetros

### Física do Fluido

Edite `config.py`:

```python
FLUID_CONFIG = {
    'num_particles': 500,        # Mais partículas = mais realista mas mais lento
    'viscosity': 0.5,            # 0.1 = água, 2.0 = mel
    'gravity': [0.0, -9.8, 0.0], # Gravidade (m/s²)
}
```

**Presets sugeridos:**

**Água:**
```python
'viscosity': 0.1,
'rest_density': 1000.0,
```

**Mel:**
```python
'viscosity': 2.0,
'rest_density': 1400.0,
```

**Óleo:**
```python
'viscosity': 1.0,
'rest_density': 900.0,
```

### Renderização

Ajuste efeitos visuais:

```python
RENDER_CONFIG = {
    'particle_size': 10.0,           # Tamanho visual das partículas
    'particle_color': [0.2, 0.5, 1.0, 0.8],  # Cor RGBA
    'enable_glow': True,             # Efeito de brilho
    'enable_motion_blur': True,      # Rastro de movimento
}
```

**Cores sugeridas:**

- Água: `[0.2, 0.5, 1.0, 0.8]` (azul)
- Fogo: `[1.0, 0.3, 0.0, 0.9]` (vermelho-laranja)
- Veneno: `[0.0, 1.0, 0.2, 0.7]` (verde)
- Energia: `[1.0, 1.0, 0.0, 0.9]` (amarelo)

### Interação

Ajuste sensibilidade dos gestos:

```python
GESTURE_CONFIG = {
    'interaction_radius': 0.15,      # Raio de influência
    'force_multiplier': 50.0,        # Força dos gestos
    'min_detection_confidence': 0.5, # Sensibilidade da detecção
}
```

### Performance

Para melhor desempenho:

```python
# Reduza partículas
FLUID_CONFIG['num_particles'] = 300

# Desabilite efeitos caros
RENDER_CONFIG['enable_glow'] = False
RENDER_CONFIG['enable_motion_blur'] = False

# Reduza resolução
VISION_CONFIG['resolution'] = (640, 480)
```

## Solução de Problemas

### Problema: "Could not start camera"

**Soluções:**
1. Verifique se a câmera está conectada
2. Teste com outro aplicativo (ex: Cheese, Webcamoid)
3. Tente mudar `camera_id` em `config.py` (0, 1, 2...)
4. Dê permissões de câmera ao terminal/Python

### Problema: "No marker detected"

**Soluções:**
1. Imprima um marcador ArUco (DICT_6X6_250)
2. Melhore a iluminação
3. Mantenha o marcador plano e sem reflexos
4. Aproxime ou afaste o marcador da câmera

### Problema: FPS baixo

**Soluções:**
1. Reduza número de partículas (200-300)
2. Desabilite efeitos visuais (glow, motion blur)
3. Reduza resolução da câmera
4. Feche outros aplicativos
5. Use um computador mais potente

### Problema: Gestos não são reconhecidos

**Soluções:**
1. Melhore a iluminação
2. Use fundo liso (evite padrões complexos)
3. Mantenha mão bem visível
4. Ajuste `min_detection_confidence` em `config.py`
5. Teste com `test_gesture_recognition.py`

### Problema: Simulação instável

**Soluções:**
1. Aumente `smoothing_radius` em `config.py`
2. Reduza `time_step` para 0.01
3. Reduza `gas_constant` para 1000.0
4. Aumente `damping` para 0.98

## Casos de Uso

### 1. Educação

Use para demonstrar:
- Dinâmica de fluidos
- Métodos numéricos (SPH)
- Física computacional
- Realidade aumentada

**Sugestão:** Use o modo demo em aula, ajuste `viscosity` para mostrar diferentes fluidos.

### 2. Arte Digital

Crie instalações interativas:
- Configure cores personalizadas
- Ajuste número de partículas
- Use diferentes gestos para efeitos

**Sugestão:** Use `particle_color` vibrante e `enable_glow: True`.

### 3. Pesquisa

Experimente com:
- Diferentes kernels SPH
- Novos métodos de integração
- Técnicas de otimização

**Sugestão:** Modifique `sph_simulator.py` e compare resultados.

### 4. Prototipagem

Base para:
- Jogos com física de fluidos
- Aplicações VR/AR
- Simuladores especializados

**Sugestão:** Use a arquitetura modular para adicionar features.

## Recursos Avançados

### Gravação de Vídeo

Para gravar a simulação, use software externo como:
- OBS Studio
- SimpleScreenRecorder
- FFmpeg

Ou adicione ao código:

```python
# No main loop
out = cv2.VideoWriter('output.avi', 
                      cv2.VideoWriter_fourcc(*'XVID'),
                      30, (width, height))
# ...
out.write(frame)
```

### Múltiplas Câmeras

Para usar múltiplas câmeras:

```python
# Modifique main.py para criar múltiplos CameraCapture
camera1 = CameraCapture(camera_id=0)
camera2 = CameraCapture(camera_id=1)
```

### Profiling

Para analisar performance:

```python
python -m cProfile -o output.prof main.py
python -m pstats output.prof
```

## Contribuindo

Quer adicionar features? Veja `DEVELOPMENT.md` para detalhes sobre a arquitetura do código.

## Suporte

- GitHub Issues: [Link para Issues]
- Documentação: `DEVELOPMENT.md`
- Exemplos: pasta `examples/`

---

**Divirta-se explorando física de fluidos em AR! 🌊✨**
