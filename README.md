# AR Fluid Vision - Real-Time Augmented Fluid Dynamics Simulation

🌊 **Simulador avançado de fluidos em Realidade Aumentada** que combina física computacional, visão computacional e interação inteligente para criar experiências imersivas e realistas.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![OpenCV](https://img.shields.io/badge/OpenCV-4.5+-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## 🎯 Características Principais

- **Simulação Física em Tempo Real**: Implementação do método SPH (Smoothed Particle Hydrodynamics) para simulação realista de fluidos
- **Detecção de Superfícies**: Detecta e rastreia superfícies do ambiente usando marcadores ArUco e detecção de planos
- **Reconhecimento de Gestos**: Interação intuitiva através de gestos das mãos usando MediaPipe
- **Renderização AR**: Visualização de partículas fluidas sobrepostas ao feed da câmera com efeitos de brilho e motion blur
- **Interação Inteligente**: Permite interação com gestos, objetos e movimento para manipular o fluido em tempo real

## 🏗️ Arquitetura do Sistema

```
AR-Fluid-Vision/
├── config.py                      # Configurações do sistema
├── main.py                        # Aplicação principal
├── requirements.txt               # Dependências Python
├── src/
│   ├── fluid_physics/            # Motor de física de fluidos
│   │   └── sph_simulator.py      # Simulador SPH
│   ├── computer_vision/          # Módulo de visão computacional
│   │   └── surface_detector.py   # Detecção de superfícies e AR tracking
│   ├── ar_renderer/              # Renderizador AR
│   │   └── particle_renderer.py  # Renderização de partículas
│   ├── interaction/              # Sistema de interação
│   │   └── gesture_recognition.py # Reconhecimento de gestos
│   └── utils/                    # Utilitários
│       └── helpers.py            # Funções auxiliares
└── examples/                     # Exemplos e testes
    ├── basic_simulation.py       # Simulação básica sem AR
    ├── test_gesture_recognition.py
    └── test_aruco_detection.py
```

## 🚀 Instalação

### Requisitos

- Python 3.8 ou superior
- Webcam ou câmera USB
- (Opcional) Marcadores ArUco impressos para melhor tracking AR

### Passos de Instalação

1. **Clone o repositório**:
```bash
git clone https://github.com/matheussiqueirahub/AR-Fluid-Vision-Real-Time-Augmented-Fluid-Dynamics-Simulation.git
cd AR-Fluid-Vision-Real-Time-Augmented-Fluid-Dynamics-Simulation
```

2. **Crie um ambiente virtual** (recomendado):
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

3. **Instale as dependências**:
```bash
pip install -r requirements.txt
```

## 💻 Uso

### Aplicação Principal

Execute a aplicação completa com AR:

```bash
python main.py
```

**Controles:**
- `ESPAÇO` - Pausar/Retomar simulação
- `R` - Resetar simulação
- `D` - Alternar informações de debug
- `Q` ou `ESC` - Sair

### Exemplos

#### 1. Simulação Básica (sem câmera)
```bash
cd examples
python basic_simulation.py
```

#### 2. Teste de Reconhecimento de Gestos
```bash
cd examples
python test_gesture_recognition.py
```

#### 3. Teste de Detecção ArUco
```bash
cd examples
python test_aruco_detection.py
```

## 🔧 Configuração

Edite `config.py` para ajustar os parâmetros do sistema:

### Parâmetros de Física de Fluidos
```python
FLUID_CONFIG = {
    'num_particles': 500,           # Número de partículas
    'particle_mass': 0.02,          # Massa de cada partícula
    'rest_density': 1000.0,         # Densidade de repouso
    'viscosity': 0.5,               # Viscosidade do fluido
    'gravity': [0.0, -9.8, 0.0],   # Vetor de gravidade
}
```

### Parâmetros de Visão Computacional
```python
VISION_CONFIG = {
    'camera_id': 0,                 # ID da câmera
    'resolution': (1280, 720),      # Resolução
    'fps': 30,                      # FPS da câmera
}
```

### Parâmetros de Renderização
```python
RENDER_CONFIG = {
    'particle_size': 10.0,          # Tamanho das partículas
    'particle_color': [0.2, 0.5, 1.0, 0.8],  # Cor RGBA
    'enable_glow': True,            # Efeito de brilho
    'enable_motion_blur': True,     # Motion blur
}
```

## 🎨 Gestos Reconhecidos

O sistema reconhece os seguintes gestos:

- **Dedo indicador**: Força direcional (empurrar)
- **Mão aberta**: Atração (puxar partículas)
- **Punho fechado**: Repulsão forte
- **Sinal de paz (V)**: Força extra forte

## 🔬 Fundamentos Técnicos

### Smoothed Particle Hydrodynamics (SPH)

A simulação utiliza o método SPH, que representa o fluido como um conjunto de partículas. Para cada partícula, calculamos:

1. **Densidade**: Usando o kernel Poly6
2. **Pressão**: Equação de estado dos gases
3. **Forças**: Pressão (kernel Spiky) e viscosidade

### Equações Principais

**Densidade:**
```
ρᵢ = Σⱼ mⱼ W(rᵢⱼ, h)
```

**Pressão:**
```
pᵢ = k(ρᵢ - ρ₀)
```

**Força de Pressão:**
```
fᵢᵖ = -Σⱼ mⱼ (pᵢ + pⱼ)/(2ρⱼ) ∇W(rᵢⱼ, h)
```

## 📊 Desempenho

O sistema é otimizado para rodar em tempo real:

- **Taxa de atualização**: ~60 FPS (dependendo do hardware)
- **Número de partículas**: Até 1000 partículas em hardware moderno
- **Latência de interação**: < 50ms

## 🤝 Contribuindo

Contribuições são bem-vindas! Por favor:

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/NovaFuncionalidade`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/NovaFuncionalidade`)
5. Abra um Pull Request

## 📝 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 🎓 Aplicações

Este sistema pode ser usado para:

- **Pesquisa**: Estudo de dinâmica de fluidos e métodos numéricos
- **Educação**: Demonstração visual de conceitos de física
- **Arte Digital**: Criação de instalações interativas
- **Prototipagem**: Desenvolvimento de aplicações AR/VR
- **Entretenimento**: Jogos e experiências imersivas

## 📚 Referências

- Müller, M., et al. "Particle-Based Fluid Simulation for Interactive Applications" (2003)
- Monaghan, J.J. "Smoothed Particle Hydrodynamics" (2005)
- MediaPipe Hands: https://google.github.io/mediapipe/solutions/hands
- OpenCV ArUco: https://docs.opencv.org/master/d5/dae/tutorial_aruco_detection.html

## 👨‍💻 Autor

**Matheus Siqueira**
- GitHub: [@matheussiqueirahub](https://github.com/matheussiqueirahub)

## 🙏 Agradecimentos

Agradecimentos especiais às comunidades de código aberto que tornaram este projeto possível:
- OpenCV
- MediaPipe
- NumPy/SciPy
- Python

---

**⭐ Se este projeto foi útil, considere dar uma estrela!**
