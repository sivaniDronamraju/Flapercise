# Flapercise

Flapercise is a gesture-controlled version of Flappy Bird game. Built using **OpenCV**, **MediaPipe**, and **Pygame**, this version lets you flap by **jumping in real life** and **raise your left hand to start or restart**. It's fun, active, and a little workout-friendly!


## To start the game
1. Clone the repo
2. Activate your environment
3. The core dependencies are:

- `pygame==2.6.1`
- `opencv-python`
- `mediapipe`

4. Install all dependencies using:
```
pip install -r requirements.txt
```
5. To run the game:
```
python main.py
```
## Game Controls & Gestures

- Start Game: Raise your left hand until the 5 sec countdown begins.
- Flap (Jump): Physically jump in front of your webcam.
- Restart Game: After a crash, raise your left hand again to restart.

## Notes

1. `scores.json` stores leaderboard information and updates after each game.
2. Ensure you’re in a well-lit room with your upper body clearly visible to the webcam.
3. Try to stand in roughly the same position when starting or restarting your jump is tracked via hip position.
4. Recommended Python version: 3.10 (MediaPipe may have issues on 3.11+).
5. When the game starts, enter your name, then feel free to **move the game window** (not the webcam feed) to get your view right.
6. To exit the game, press ESC

## Credits
Game logic and sprite assets adapted from the original open-source project: [sourabhv/FlapPyBird](https://github.com/sourabhv/FlapPyBird).  
This version adds motion control, gesture recognition, and MediaPipe-powered body tracking.