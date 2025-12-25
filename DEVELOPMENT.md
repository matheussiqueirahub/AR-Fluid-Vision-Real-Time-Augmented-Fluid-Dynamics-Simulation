# Guia de Desenvolvimento - AR Fluid Vision

## Estrutura do Código

### Módulos Principais

#### 1. Fluid Physics (`src/fluid_physics/`)

**sph_simulator.py**: Implementa a simulação SPH (Smoothed Particle Hydrodynamics)

Classes principais:
- `Particle`: Representa uma partícula individual do fluido
- `SPHFluidSimulator`: Gerencia toda a simulação de fluidos

Métodos importantes:
- `_compute_density_pressure()`: Calcula densidade e pressão usando kernels SPH
- `_compute_forces()`: Calcula forças de pressão e viscosidade
- `_integrate()`: Integração temporal usando método semi-implícito de Euler
- `add_external_force()`: Aplica forças externas (interação do usuário)

#### 2. Computer Vision (`src/computer_vision/`)

**surface_detector.py**: Detecção de superfícies e tracking AR

Classes principais:
- `SurfaceDetector`: Detecta marcadores ArUco e planos
- `CameraCapture`: Gerencia captura de vídeo da câmera

Métodos importantes:
- `detect_aruco_markers()`: Detecta e estima pose de marcadores ArUco
- `project_3d_to_2d()`: Projeta coordenadas 3D do mundo para 2D da tela
- `get_world_transform()`: Obtém matriz de transformação câmera-mundo

#### 3. AR Renderer (`src/ar_renderer/`)

**particle_renderer.py**: Renderização de partículas com efeitos visuais

Classes principais:
- `ARFluidRenderer`: Renderiza partículas com efeitos de brilho e motion blur
- `SimpleRenderer`: Renderizador alternativo simplificado

Métodos importantes:
- `render_particles_2d()`: Renderiza partículas na tela
- `_draw_glowing_particle()`: Desenha partícula com efeito de brilho
- `add_hud()`: Adiciona informações na tela

#### 4. Interaction (`src/interaction/`)

**gesture_recognition.py**: Reconhecimento de gestos e interação

Classes principais:
- `GestureRecognizer`: Detecta mãos e reconhece gestos usando MediaPipe
- `ObjectInteraction`: Detecta e rastreia objetos para colisão

Métodos importantes:
- `process_frame()`: Processa frame para detectar mãos
- `_detect_gesture()`: Identifica tipo de gesto
- `get_interaction_forces()`: Converte gestos em forças para a simulação

#### 5. Utils (`src/utils/`)

**helpers.py**: Funções auxiliares e utilitários

Classes e funções:
- `FPSCounter`: Contador de FPS
- `PerformanceMonitor`: Monitor de desempenho
- `SpatialHashGrid`: Grid espacial para otimização de busca de vizinhos

## Fluxo de Dados

```
Câmera → Frame
    ↓
SurfaceDetector → ArUco Pose
    ↓
GestureRecognizer → Hand Positions + Gestures
    ↓
SPHFluidSimulator ← External Forces
    ↓
Particle Positions (3D)
    ↓
SurfaceDetector.project_3d_to_2d()
    ↓
Particle Positions (2D)
    ↓
ARFluidRenderer → Rendered Frame
    ↓
Display
```

## Adicionando Novas Funcionalidades

### 1. Novo Tipo de Partícula

Para adicionar um novo tipo de partícula:

1. Estenda a classe `Particle` em `sph_simulator.py`:
```python
class CustomParticle(Particle):
    def __init__(self, position):
        super().__init__(position)
        self.custom_property = 0.0
```

2. Modifique `SPHFluidSimulator` para usar a nova classe

### 2. Novo Gesto

Para adicionar reconhecimento de um novo gesto:

1. Modifique `_detect_gesture()` em `gesture_recognition.py`:
```python
def _detect_gesture(self, hand_landmarks):
    # ... código existente ...
    
    # Novo gesto: polegar + mindinho estendidos
    thumb_extended = ...
    pinky_extended = ...
    
    if thumb_extended and pinky_extended and not index_extended:
        self.gesture_type = "rock_sign"
```

2. Adicione comportamento em `get_interaction_forces()`:
```python
if self.gesture_type == "rock_sign":
    force_magnitude *= 3.0  # Força customizada
```

### 3. Novo Efeito Visual

Para adicionar um novo efeito de renderização:

1. Adicione método em `ARFluidRenderer`:
```python
def _draw_custom_effect(self, overlay, position, size):
    # Implemente seu efeito visual
    pass
```

2. Integre no método `render_particles_2d()`

## Otimização de Desempenho

### Dicas para Melhor Performance

1. **Reduzir número de partículas**:
```python
FLUID_CONFIG['num_particles'] = 300  # Ao invés de 500
```

2. **Aumentar smoothing radius** (menos cálculos por partícula):
```python
FLUID_CONFIG['smoothing_radius'] = 0.08  # Ao invés de 0.05
```

3. **Desabilitar efeitos visuais caros**:
```python
RENDER_CONFIG['enable_glow'] = False
RENDER_CONFIG['enable_motion_blur'] = False
```

4. **Usar Spatial Hash Grid** (já implementado, mas pode ser otimizado):
   - Implemente em `SPHFluidSimulator._compute_forces()` para busca eficiente de vizinhos

### Profiling

Use o `PerformanceMonitor` para identificar gargalos:

```python
monitor = PerformanceMonitor()

monitor.start_timer('physics')
# código de física
physics_time = monitor.end_timer('physics')

print(f"Physics took {physics_time*1000:.2f}ms")
```

## Testes

### Executando Testes Unitários

(A serem implementados)

```bash
python -m pytest tests/
```

### Testes Manuais

Use os exemplos na pasta `examples/`:

1. `basic_simulation.py`: Testa física sem AR
2. `test_gesture_recognition.py`: Testa detecção de mãos
3. `test_aruco_detection.py`: Testa tracking AR

## Debugging

### Modo Debug

Ative informações detalhadas em `config.py`:

```python
DEBUG_CONFIG = {
    'show_fps': True,
    'show_particle_count': True,
    'show_boundaries': True,
    'show_hand_landmarks': True,
    'verbose': True,  # Mostra tempos de cada módulo
}
```

### Logs Comuns

- "Could not start camera": Verifique se a câmera está conectada e não está sendo usada por outro aplicativo
- "No marker detected": Imprima ou mostre um marcador ArUco DICT_6X6_250
- Performance baixa: Reduza número de partículas ou desabilite efeitos visuais

## Calibração da Câmera

Para melhor precisão AR, calibre sua câmera:

1. Use o script de calibração do OpenCV
2. Obtenha `camera_matrix` e `dist_coeffs`
3. Substitua em `surface_detector.py`:

```python
self.camera_matrix = np.array([
    [fx, 0, cx],
    [0, fy, cy],
    [0, 0, 1]
])
self.dist_coeffs = np.array([k1, k2, p1, p2, k3])
```

## Contribuindo

1. Siga o estilo de código PEP 8
2. Adicione docstrings para novas classes e métodos
3. Teste suas mudanças com os exemplos
4. Documente novas funcionalidades no README

## Recursos Adicionais

- [Documentação SPH](https://matthias-research.github.io/pages/publications/sca03.pdf)
- [MediaPipe Hands](https://google.github.io/mediapipe/solutions/hands.html)
- [OpenCV ArUco](https://docs.opencv.org/4.x/d5/dae/tutorial_aruco_detection.html)
