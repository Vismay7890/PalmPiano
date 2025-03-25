import cv2
import threading
import pygame.midi
import time
from cvzone.HandTrackingModule import HandDetector

# 🎹 Initialize Pygame MIDI (same as before)
pygame.midi.init()
print("MIDI initialized")

if pygame.midi.get_count() == 0:
    print("❌ No MIDI output devices found!")
    pygame.midi.quit()
    exit()
else:
    print("✅ MIDI output devices found:")
    for i in range(pygame.midi.get_count()):
        print(f"  Device {i}: {pygame.midi.get_device_info(i)}")

try:
    player = pygame.midi.Output(0)
    print("✅ MIDI Output port opened successfully (Device 0)")
except pygame.midi.MidiException as e:
    print(f"❌ Error opening MIDI output port: {e}")
    pygame.midi.quit()
    exit()

# 🎼 Instrument List (same as before)
instruments = [
    (0, "Acoustic Grand Piano"),
    (24, "Acoustic Guitar (nylon)"),
    (40, "Violin"),
    (48, "String Ensemble 1"),
    (81, "Lead Square Wave (Synth)")
]
current_instrument_index = 0
player.set_instrument(instruments[current_instrument_index][0])
print(f"🎹 Instrument set to: {instruments[current_instrument_index][1]}")

# 🎐 Initialize Hand Detector (same as before)
cap = cv2.VideoCapture(0)
detector = HandDetector(detectionCon=0.8)

# 🎺 Chord Mapping - Load from file (same as before)
def load_chord_mapping(filepath="chords.txt"):
    chord_map = {"left": {}, "right": {}}
    try:
        with open(filepath, 'r') as file:
            next(file)
            for line in file:
                parts = line.strip().split(',')
                if len(parts) == 6:
                    hand, finger, chord_name, note1, note2, note3 = parts
                    hand = hand.strip().lower()
                    finger = finger.strip().lower()

                    def note_to_midi(note_name):
                        note_map = {'c': 60, 'd': 62, 'e': 64, 'f': 65, 'g': 67, 'a': 69, 'b': 71}
                        note_name = note_name.lower().replace('#', 's')
                        base_note = note_name[0]
                        octave_offset = int(note_name[1:]) - 4 if len(note_name) > 1 and note_name.isdigit() else 0

                        if base_note in note_map:
                           midi_note = note_map[base_note] + (12 * octave_offset)
                           if 's' in note_name:
                               midi_note += 1
                           return midi_note
                        return None

                    notes = [note_to_midi(note1.strip()), note_to_midi(note2.strip()), note_to_midi(note3.strip())]
                    notes = [note for note in notes if note is not None]

                    if hand in chord_map and finger in ["thumb", "index", "middle", "ring", "pinky"] and notes:
                        chord_map[hand][finger] = notes
                    else:
                        print(f"Warning: Invalid chord mapping entry: {line.strip()}")
                else:
                    print(f"Warning: Invalid line format in chord mapping file: {line.strip()}")
    except FileNotFoundError:
        print(f"Error: Chord mapping file '{filepath}' not found.")
        return None

    return chord_map

chords = load_chord_mapping()

if chords is None:
    exit()

print("🎼 Chord mapping loaded successfully:")
print(chords)

# Sustain Time (same as before)
SUSTAIN_TIME = 0.2

# Track Previous States for Chords (same as before)
prev_states = {hand: {finger: 0 for finger in chords[hand]} for hand in chords}

# 🎵 Functions to Play/Stop Chord (same as before)
def play_chord(chord_notes):
    print(f"Playing chord notes: {chord_notes}")
    for note in chord_notes:
        if 0 <= note <= 127:
            player.note_on(note, 127)
        else:
            print(f"⚠️ Warning: Note {note} is outside MIDI range (0-127). Ignoring.")

def stop_chord_after_delay(chord_notes):
    time.sleep(SUSTAIN_TIME)
    for note in chord_notes:
        if 0 <= note <= 127:
            player.note_off(note, 127)

# --- Instrument Switching Variables ---
current_instrument_name = instruments[current_instrument_index][1]
instrument_switch_gesture_active = False # Flag to track if the gesture is active
instrument_switch_start_time = 0       # Time when the gesture started
INSTRUMENT_SWITCH_HOLD_TIME = 0.5      # Time (seconds) to hold gesture for switch

# --- Chord Name and Instrument Display Variables (same as before) ---
current_chord_name = ""


while True:
    success, img = cap.read()
    if not success:
        print("❌ Camera not capturing frames")
        continue

    img = cv2.flip(img, 1)
    hands, img = detector.findHands(img, draw=True)

    played_chord_this_frame = False
    instrument_switched_this_frame = False

    if hands:
        if len(hands) == 2:
            hand1_fingers_up = detector.fingersUp(hands[0])
            hand2_fingers_up = detector.fingersUp(hands[1])
            if hand1_fingers_up == [1, 1, 1, 1, 1] and hand2_fingers_up == [1, 1, 1, 1, 1]: # Both hands all fingers up gesture detected

                if not instrument_switch_gesture_active: # Gesture just became active
                    instrument_switch_gesture_active = True
                    instrument_switch_start_time = time.time() # Record start time
                    print("Instrument switch gesture ACTIVE - Hold for 0.5 seconds...") # Feedback

                else: # Gesture is still active, check hold time
                    if time.time() - instrument_switch_start_time >= INSTRUMENT_SWITCH_HOLD_TIME: # Held long enough
                        if not instrument_switched_this_frame: # Debounce switch
                            current_instrument_index = (current_instrument_index + 1) % len(instruments)
                            player.set_instrument(instruments[current_instrument_index][0])
                            current_instrument_name = instruments[current_instrument_index][1]
                            print(f"🎹 Instrument switched to: {current_instrument_name}")
                            instrument_switched_this_frame = True # Prevent multiple switches in one hold
                            instrument_switch_gesture_active = False # Reset gesture active flag after switch

            else: # Gesture is not active (fingers not all up on both hands)
                instrument_switch_gesture_active = False # Reset gesture active flag
                if instrument_switched_this_frame: # Reset the debounce flag for next switch
                    instrument_switched_this_frame = False

        else: # Only one hand or no hands, reset instrument switch gesture
             instrument_switch_gesture_active = False
             instrument_switched_this_frame = False


        for hand in hands: # Chord playing logic (same as before)
            hand_type = "left" if hand["type"] == "Left" else "right"
            fingers = detector.fingersUp(hand)
            finger_names = ["thumb", "index", "middle", "ring", "pinky"]

            for i, finger in enumerate(finger_names):
                if finger in chords[hand_type]:
                    if fingers[i] == 1 and prev_states[hand_type][finger] == 0:
                        chord_to_play = chords[hand_type][finger]
                        play_chord(chord_to_play)
                        current_chord_finger_name = finger.capitalize()
                        current_chord_hand_type = hand_type.capitalize()
                        for line in open("chords.txt", 'r'):
                            parts = line.strip().split(',')
                            if len(parts) == 6 and parts[0].strip().lower() == hand_type and parts[1].strip().lower() == finger:
                                current_chord_name = f"{parts[2].strip()} ({current_chord_hand_type} {current_chord_finger_name})"
                                break
                        played_chord_this_frame = True

                    elif fingers[i] == 0 and prev_states[hand_type][finger] == 1:
                        chord_to_stop = chords[hand_type][finger]
                        threading.Thread(target=stop_chord_after_delay, args=(chord_to_stop,), daemon=True).start()
                    prev_states[hand_type][finger] = fingers[i]
    else: # No hands detected (same as before)
        if any(any(state.values()) for state in prev_states.values()):
            for hand in chords:
                for finger in chords[hand]:
                    if prev_states[hand][finger] == 1:
                        threading.Thread(target=stop_chord_after_delay, args=(chords[hand][finger],), daemon=True).start()
            prev_states = {hand: {finger: 0 for finger in chords[hand]} for hand in chords}
        current_chord_name = ""
        instrument_switched_this_frame = False # Reset debounce flag when no hands
        instrument_switch_gesture_active = False # Reset gesture flag


    # --- Display Chord and Instrument (same as before) ---
    display_text = ""
    if current_chord_name and played_chord_this_frame:
        display_text = current_chord_name
    elif current_chord_name:
        display_text = "(Sustaining) " + current_chord_name

    if display_text:
        cv2.putText(img, display_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2, cv2.LINE_AA)

    cv2.putText(img, f"Instrument: {current_instrument_name}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 200, 200), 2, cv2.LINE_AA)

    # --- Visual Feedback for Instrument Switch Gesture ---
    if instrument_switch_gesture_active:
        cv2.putText(img, "Hold to Switch Instrument...", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2, cv2.LINE_AA) # Yellow text


    cv2.imshow("Hand Tracking MIDI Chords", img)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
pygame.midi.quit()