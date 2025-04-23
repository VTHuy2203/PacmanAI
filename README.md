# 🧠 Pacman AI Game (Python + Pygame)

A 2D **Pacman game with AI** built using **Python** and **Pygame**. Pacman can be controlled manually or move intelligently using **A\*** pathfinding to avoid ghosts and collect food safely.

## 🎮 Game Features

- 🔁 Two Modes:
  - **Manual Mode**: Use arrow keys to control Pacman.
  - **AI Mode**: Pacman automatically collects food while avoiding the ghost.
- 🧠 Smart AI:
  - Uses **A\*** algorithm to find shortest and safest path.
  - Avoids dangerous paths if ghost is nearby.
- 👻 Ghost follows Pacman using basic tracking logic.
- 🍕 Randomly placed food items across the map.
- 🎨 Simple retro graphics using Pygame.
- ⚰️ Game over on collision with ghost.
- ✅ Win when all food is collected.

## 🧪 Technologies Used

- [Python 3](https://www.python.org/)
- [Pygame](https://www.pygame.org/)
- A\* Pathfinding Algorithm

## 📷 Screenshots

*(Add screenshots here, if available)*

## 🚀 How to Run

### 1. Clone the repository

```bash
git clone https://github.com/your-username/pacman-ai.git
cd pacman-ai

2. Install requirements
-----pip install pygame
3. Run the game
-----python pacman_ai.py

⌨️ Controls

Action	Key
Move Up	↑ Arrow
Move Down	↓ Arrow
Move Left	← Arrow
Move Right	→ Arrow
Pause Game	P
Choose AI/Manual	Menu at start

🧠 AI Logic Explained
Pacman evaluates surrounding tiles using A* search.

If ghost is near, Pacman prioritizes reaching a safe zone.

Otherwise, Pacman moves towards nearest safe food.

Ghost chases Pacman using greedy pathfinding.

🛠️ Customization Ideas
Add more ghosts with smarter AI.

Power-ups: invincibility, speed boost.

Maze randomizer.

Lives system.

📄 License
MIT License © 2025 Trọng Huy

