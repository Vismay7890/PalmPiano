import cv2
import threading
import pygame.midi
import time
from cvzone.HandTrackingModule import HandDetector

# 🎹 Initialize Pygame MIDI
pygame.midi.init()
# print("MIDI initialized") # DEBUG

# Check for MIDI output devices
if pygame.midi.get_count() == 0:
    # print("❌ No MIDI output devices found!")
    pygame.midi.quit()
    exit()
else:
    # print("✅ MIDI output devices found:")
    for i in range(pygame.midi.get_count()):
        print(f"  Device {i}: {pygame.midi.get_device_info(i)}")

try:
    player = pygame.midi.Output(0) # Try opening the first output device
    # print("✅ MIDI Output port opened successfully (Device 0)") # DEBUG
except pygame.midi.MidiException as e:
    # print(f"❌ Error opening MIDI output port: {e}")
    pygame.midi.quit()
    exit()

player.set_instrument(0)  # 0 = Acoustic Grand Piano
print("🎹 Instrument set to Acoustic Grand Piano") # DEBUG

# 🎐 Initialize Hand Detector
cap = cv2.VideoCapture(0)
detector = HandDetector(detectionCon=0.8)

# 🎺 Chord Mapping - Load from file
def load_chord_mapping(filepath="chords.txt"):
    chord_map = {"left": {}, "right": {}}
    try:
        with open(filepath, 'r') as file:
            next(file)  # Skip header line
            for line in file:
                parts = line.strip().split(',') # Use comma as delimiter if your txt is CSV-like
                if len(parts) == 6:  # Expecting 6 columns now! <---- CHANGED TO 6
                    hand, finger, chord_name, note1, note2, note3 = parts
                    hand = hand.strip().lower()
                    finger = finger.strip().lower()

                    # Convert note names to MIDI numbers (you might need a helper function or dictionary)
                    def note_to_midi(note_name): # Simple helper for now, improve if needed for sharps/flats
                        note_map = {'c': 60, 'd': 62, 'e': 64, 'f': 65, 'g': 67, 'a': 69, 'b': 71} # Octave 4 as base
                        note_name = note_name.lower().replace('#', 's') # replace # with s for sharps (midi-note friendly names)
                        base_note = note_name[0]
                        octave_offset = int(note_name[1:]) - 4 if len(note_name) > 1 and note_name[1:].isdigit() else 0 # Assuming octave is specified like D4, C5, etc. and is digit

                        if base_note in note_map:
                           midi_note = note_map[base_note] + (12 * octave_offset)

                           # Handle Sharps (crude, assumes only single sharp after note letter)
                           if 's' in note_name:
                               midi_note += 1

                           return midi_note
                        return None # Handle invalid note names

                    notes = [note_to_midi(note1.strip()), note_to_midi(note2.strip()), note_to_midi(note3.strip())]
                    notes = [note for note in notes if note is not None] # Filter out None values if note_to_midi fails

                    if hand in chord_map and finger in ["thumb", "index", "middle", "ring", "pinky"] and notes: #Basic finger validation
                        chord_map[hand][finger] = notes
                    else:
                        print(f"Warning: Invalid chord mapping entry: {line.strip()}") # Keep this warning, it's still useful for other issues
                else:
                    print(f"Warning: Invalid line format in chord mapping file: {line.strip()}") # Keep this warning, it's still useful for truly malformed lines
    except FileNotFoundError:
        print(f"Error: Chord mapping file '{filepath}' not found.")
        return None # Or return a default empty mapping, or exit, depending on how critical the file is

    return chord_map

chords = load_chord_mapping()

if chords is None: # Exit if chord mapping couldn't be loaded
    exit()


# Sustain Time (in seconds) after the finger is lowered
SUSTAIN_TIME = 0.2  # Reduced sustain for faster response, adjust as needed

# Track Previous States to Stop Chords
prev_states = {hand: {finger: 0 for finger in chords[hand]} for hand in chords}

# 🎵 Function to Play a Chord
def play_chord(chord_notes):
    for note in chord_notes:
        if 0 <= note <= 127: # Validate note range (MIDI notes are 0-127)
            player.note_on(note, 127)  # Start playing
        else:
            print(f"⚠️ Warning: Note {note} is outside MIDI range (0-127). Ignoring.")


# 🎵 Function to Stop a Chord After a Delay
def stop_chord_after_delay(chord_notes):
    time.sleep(SUSTAIN_TIME)  # Sustain for specified time
    for note in chord_notes:
        if 0 <= note <= 127: # Validate note range before stopping too
            player.note_off(note, 127)  # Stop playing
        # No warning needed here for out-of-range notes on note_off, as it might be a previous range issue


# --- Add a variable to store the currently played chord name for display ---
current_chord_name = ""


while True:
    success, img = cap.read()
    if not success:       
        continue

    img = cv2.flip(img, 1) # Flip horizontally for natural mirroring
    hands, img = detector.findHands(img, draw=True)

    played_chord_this_frame = False # Flag to track if any chord was played in this frame

    if hands:
        for hand in hands:
            hand_type = "left" if hand["type"] == "Left" else "right"
            fingers = detector.fingersUp(hand)
            finger_names = ["thumb", "index", "middle", "ring", "pinky"]

            for i, finger in enumerate(finger_names):
                if finger in chords[hand_type]:  # Only check assigned chords
                    if fingers[i] == 1 and prev_states[hand_type][finger] == 0:
                        chord_to_play = chords[hand_type][finger]
                        play_chord(chord_to_play)  # Play chord
                        # --- Update current chord name for display ---
                        current_chord_finger_name = finger.capitalize() # Get finger name for display
                        current_chord_hand_type = hand_type.capitalize()
                        # Find the chord name from the mapping (not efficient for large mappings, but okay for now)
                        for line in open("chords.txt", 'r'):
                            parts = line.strip().split(',')
                            if len(parts) == 5 and parts[0].strip().lower() == hand_type and parts[1].strip().lower() == finger:
                                current_chord_name = f"{parts[2].strip()} ({current_chord_hand_type} {current_chord_finger_name})"
                                break # Stop searching once found
                        played_chord_this_frame = True # Set the flag

                    elif fingers[i] == 0 and prev_states[hand_type][finger] == 1:
                        chord_to_stop = chords[hand_type][finger]
                        threading.Thread(target=stop_chord_after_delay, args=(chord_to_stop,), daemon=True).start()
                    prev_states[hand_type][finger] = fingers[i]  # Update state
    else:
        # If no hands detected, stop all chords after delay (less aggressive stopping)
        if any(any(state.values()) for state in prev_states.values()): # Only stop if any chord was playing
            for hand in chords:
                for finger in chords[hand]:
                    if prev_states[hand][finger] == 1: # Only stop if it was playing
                        threading.Thread(target=stop_chord_after_delay, args=(chords[hand][finger],), daemon=True).start()
            prev_states = {hand: {finger: 0 for finger in chords[hand]} for hand in chords}
        current_chord_name = "" # Clear chord name when no hands detected


    # --- Display Chord Name on Screen ---
    if current_chord_name and played_chord_this_frame: # Only display if a chord was played in this frame
        cv2.putText(img, current_chord_name, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2, cv2.LINE_AA)
    elif current_chord_name: # If chord name is still set but no chord played this frame (might be sustaining)
        cv2.putText(img, "(Sustaining) " + current_chord_name, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (150, 150, 150), 2, cv2.LINE_AA) # Greyed out sustain indication


    cv2.imshow("Hand Tracking MIDI Chords", img)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
pygame.midi.quit()