# Hand Gesture Piano

A fun project that turns your hand gestures into piano music! Using hand tracking and Python, this program allows you to play chords on a virtual piano by simply raising different fingers. You can even switch instruments with a special hand gesture!

## Features

*   **Real-time Hand Tracking:** Uses your webcam to detect hand and finger positions.
*   **Chord Recognition:** Maps specific finger gestures to musical chords (currently based on the D Major scale, expandable!).
*   **MIDI Output:** Plays piano and other instrument sounds through your computer's MIDI output.
*   **Instrument Switching:** Change the instrument sound by holding up both hands with all fingers extended. Cycles through a list of instruments.
*   **Visual Feedback:** Displays the detected chord name and current instrument on the video feed.
*   **Sustain Effect:** Notes sustain briefly after you lower your fingers for a smoother musical experience.

## Getting Started

Follow these steps to get the Hand Gesture Piano up and running on your machine.

### Prerequisites

*   **Python 3.7 or higher:** Make sure you have Python installed. You can download it from [python.org](https://www.python.org/downloads/).
*   **pip:** Python's package installer, usually included with Python installations.
*   **Webcam:**  A working webcam connected to your computer.
*   **MIDI Output:**  Your computer's default audio output might work as a MIDI output. If you want to use external MIDI devices or virtual MIDI ports, ensure they are set up on your system. (For virtual MIDI ports on Windows, consider [loopMIDI](https://www.tobias-erichsen.de/software/loopmidi.html)).

### Installation

1.  **Clone the repository (or download the ZIP):**

    ```bash
    git clone https://github.com/Vismay7890/PalmPiano
    cd PamPiano
    ```

2.  **Create a virtual environment (recommended):**

    ```bash
    python -m venv pianoenv
    pianoenv\Scripts\activate  # On Windows
    source pianoenv/bin/activate # On macOS/Linux
    ```

3.  **Install required Python packages:**

    ```bash
    pip install -r requirements.txt
    ```

### Usage

1.  **Make sure your webcam is connected and working.**
2.  **Run the `hand_piano.py` or `enhanced.py` script:**

    ```bash
    python hand_piano.py
    ```

3.  **A video window will open, showing your webcam feed.**
4.  **Place your hand in front of the camera.** The program will detect your hand and fingers.
5.  **Raise different fingers to play chords!** See the `chord_mapping.txt` file for the current finger-to-chord assignments.
6.  **Switch Instruments:** To change the instrument sound, raise **both hands** with **all fingers extended** and hold for about 0.5 seconds. The instrument will cycle to the next one in the instrument list.
7.  **Press `q` in the video window to quit the program.**

## Dependencies

*   **opencv-python:** For image processing and webcam access.
*   **pygame:** For MIDI output.
*   **cvzone:**  A library for simplifying Computer Vision tasks, used here for hand tracking.
*   **tensorflow (or tensorflow-cpu/tensorflow-gpu):** Required by `cvzone` for hand tracking model.

These dependencies are listed in the `requirements.txt` file.

## Chord Mapping (`chord_mapping.txt`)

The file `chord_mapping.txt` defines which chords are played by raising different fingers on each hand.

*   **Format:** Comma-separated values (CSV).
*   **Columns:** `Hand`, `Finger`, `Chord Name`, `Note1`, `Note2`, `Note3` (Note names are in format like 'D4', 'F#4', 'A4').
*   **Example:**

    ```txt
    Hand,Finger,Chord Name,Note1,Note2,Note3
    Left,Thumb,D Major,D4,F#4,A4
    Left,Index,E Minor,E4,G4,B4
    Right,Thumb,A Major,A4,C#5,E5
    ```

You can customize this file to change the chords and scales used in the project!

## Instrument Switching Gesture

*   **Gesture:** Raise **both hands** in front of the camera with **all fingers fully extended** (like a "praise" gesture). Hold for a brief moment (around 0.5 seconds).
*   **Action:**  The instrument sound will cycle to the next instrument in the predefined list.
*   **Feedback:**  "Hold to Switch Instrument..." text will appear on screen while performing the gesture. The instrument name display will update when the switch is complete.

## Future Enhancements (Ideas)

*   **Expand Chord Library:** Add more scales, modes, and chord voicings to `chord_mapping.txt`.
*   **Visual Keyboard Overlay:**  Display a virtual keyboard on the screen, highlighting the keys being played.
*   **Velocity Control:**  Make the volume of notes dependent on the speed of finger movements.
*   **Sustain Pedal Gesture:** Implement a gesture to act as a sustain pedal.
*   **Octave Control Gestures:** Add gestures to shift the octave up or down.
*   **Melody Mode:** Switch to a mode where fingers play single notes instead of chords.
*   **Rhythm and Arpeggiation:** Introduce rhythmic patterns or arpeggios for chords.
*   **Record and Playback:**  Implement recording and playback of hand gesture performances.

## License

This project is licensed under the [Your License Name] License - see the `LICENSE` file for details. (Consider using a license like MIT or Apache 2.0).

## Author

Vismay Jain - [[MY Portfolio](https://vismay-portfolio.vercel.app/)]

---

Enjoy making music with your hands! 🎉
