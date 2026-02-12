# Game Launcher App

![Python](https://img.shields.io/badge/Python-3.x-blue)
![Pygame](https://img.shields.io/badge/Pygame-Game%20Engine-green)

**Game Launcher** is a lightweight game library interface designed for games built with the **Pygame** engine.  
It allows users to browse a collection of available games and launch them instantly from a single centralized interface, eliminating the need to manually run individual game files.

The launcher is designed for simplicity, quick navigation, and seamless switching between games, making it ideal for collections of small Pygame projects or student game portfolios.

https://github.com/user-attachments/assets/51640ef3-467d-4d57-a3ed-e8b1ef2d845d

---

## Features
- Centralized library for multiple Pygame games
- One-click game launching
- Automatic detection of games inside the library folder
- Keyboard and controller navigation support
- Seamless return to the launcher after exiting a game
- Grid / list display modes (if enabled)
- Focus highlighting for improved navigation

---

## Project Structure

```bash
PyGameApp/ 
│
├── launcher.py
├── library/
│ ├── Game1/
│ │ └── game.py
│ │ └── icon.png
│ ├── Game2/
│ │ └── game.py
│ │ └── icon.png
│ └── ...
```

Each game and icon should be placed inside its own folder within the `library/` directory.

---

## Requirements
- Python 3.x
- Pygame

Install dependencies:
```bash
pip install pygame

#Run 
python game_launcher.py
```
