import pyautogui
import pyperclip
import time
import random
import threading
import sys
import re

# Try to import numpy, fall back to basic random if not available
try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False
    print("[WARNING] 📦 NumPy not found. Using basic random distribution.")
    print("[INFO] 💻 For better typing realism, install with: pip3 install numpy")

# Typing states
TYPING_STOPPED = 0
TYPING_ACTIVE = 1
TYPING_PAUSED = 2

typing_state = TYPING_STOPPED
typing_thread = None
typing_position = 0
typing_lock = threading.Lock()

# WPM Configuration
DEFAULT_BASE_WPM = 85  # Base typing speed (increased from 65)
WPM_VARIATION = 0.3    # 30% variation (±25 WPM from base)
FATIGUE_FACTOR = 0.12  # 12% slowdown over time (reduced from 15%)
BURST_CHANCE = 0.10    # 10% chance of fast burst (increased from 8%)
HESITATION_CHANCE = 0.04  # 4% chance of hesitation (reduced from 5%)

# Enhanced human-like timing with Gaussian distribution
MICRO_PAUSE_CHANCE = 0.15  # 15% chance of tiny micro-pauses
RHYTHM_VARIATION = 0.4     # 40% rhythm variation between keystrokes
TYPING_FLOW_STATES = ['steady', 'rushed', 'careful', 'thinking']

def get_typing_flow_state():
    """Randomly select a typing flow state that affects multiple characters"""
    return random.choice(TYPING_FLOW_STATES)

def human_delay_gaussian(mean_wpm=85, std_factor=0.3):
    """Generate human-like delays using Gaussian distribution or fallback"""
    # Convert WPM to character delay (5 chars per word average)
    chars_per_second = (mean_wpm * 5) / 60
    base_delay = 1.0 / chars_per_second
    
    if HAS_NUMPY:
        # Use Gaussian distribution for more natural variation
        std_delay = base_delay * std_factor
        delay = np.random.normal(base_delay, std_delay)
    else:
        # Fallback to basic random variation
        variation = base_delay * std_factor
        delay = random.uniform(base_delay - variation, base_delay + variation)
    
    # Ensure minimum delay
    return max(0.008, delay)

def clean_clipboard_text_advanced(text):
    """Enhanced text cleaning with better whitespace handling"""
    if not text:
        return text
    
    # Split into lines for processing
    lines = text.split('\n')
    cleaned_lines = []
    
    for line in lines:
        # Remove trailing whitespace from each line
        cleaned_line = line.rstrip()
        
        # Replace multiple consecutive spaces with single space (preserve intentional formatting)
        cleaned_line = re.sub(r' {2,}', ' ', cleaned_line)
        
        # Remove leading whitespace but preserve indentation (tabs/4+ spaces)
        if cleaned_line.startswith('\t') or cleaned_line.startswith('    '):
            # Preserve intentional indentation
            pass
        else:
            cleaned_line = cleaned_line.lstrip()
        
        cleaned_lines.append(cleaned_line)
    
    # Join lines back together
    cleaned_text = '\n'.join(cleaned_lines)
    
    # Remove excessive empty lines (more than 2 consecutive)
    cleaned_text = re.sub(r'\n{3,}', '\n\n', cleaned_text)
    
    # Strip leading and trailing whitespace from entire text
    cleaned_text = cleaned_text.strip()
    
    return cleaned_text

def calculate_char_delay_enhanced(base_wpm, char, position, total_chars, flow_state='steady', prev_char=None):
    """Enhanced delay calculation with Gaussian distribution and better human factors"""
    
    # Apply fatigue (gradual slowdown)
    fatigue_multiplier = 1 + (FATIGUE_FACTOR * position / total_chars)
    current_wpm = base_wpm / fatigue_multiplier
    
    # Use Gaussian distribution for more natural variation
    base_delay = human_delay_gaussian(current_wpm, WPM_VARIATION)
    
    # Flow state modifiers
    flow_modifiers = {
        'steady': 1.0,      # Normal typing
        'rushed': 0.65,     # Typing quickly (improved from 0.7)
        'careful': 1.5,     # Deliberate typing (improved from 1.4)
        'thinking': 2.0     # Thoughtful typing (improved from 1.8)
    }
    flow_modifier = flow_modifiers.get(flow_state, 1.0)
    
    # Enhanced character-specific modifiers
    char_modifier = 1.0
    
    if char in '.!?':
        char_modifier = random.uniform(2.5, 4.0)  # Sentence endings
    elif char in ',;:':
        char_modifier = random.uniform(1.4, 2.5)  # Punctuation
    elif char == ' ':
        # Context-aware space timing
        if prev_char and prev_char in '.!?':
            char_modifier = random.uniform(0.3, 0.6)  # Quick space after sentence
        elif prev_char and prev_char in ',;:':
            char_modifier = random.uniform(0.5, 0.8)  # Medium space after punctuation
        else:
            char_modifier = random.uniform(0.7, 1.1)  # Normal word spacing
    elif char.isupper() and prev_char and prev_char.islower():
        char_modifier = random.uniform(1.1, 1.4)  # Caps transition
    elif char.isdigit():
        char_modifier = random.uniform(1.2, 1.6)  # Numbers
    elif char in '()[]{}':
        char_modifier = random.uniform(1.3, 1.8)  # Brackets
    elif char in '"\'':
        char_modifier = random.uniform(1.0, 1.3)  # Quotes
    elif char in '!@#$%^&*+=<>?':
        char_modifier = random.uniform(1.4, 2.0)  # Special symbols
    elif char == '\n':
        char_modifier = random.uniform(1.5, 2.5)  # New lines
    elif char == '\t':
        char_modifier = random.uniform(1.0, 1.5)  # Tabs
    
    # Common letter combinations (enhanced)
    if prev_char:
        common_bigrams = [
            'th', 'he', 'in', 'er', 'an', 're', 'ed', 'nd', 'on', 'en', 
            'at', 'ou', 'it', 'is', 'or', 'ti', 'hi', 'st', 'io', 'le', 
            'ea', 'ng', 'ar', 've', 'te', 'co', 'to', 'al', 'de', 'se'
        ]
        bigram = (prev_char + char).lower()
        if bigram in common_bigrams:
            char_modifier *= random.uniform(0.6, 0.8)  # Faster for common patterns
        
        # Difficult combinations
        difficult_bigrams = ['qu', 'x', 'z', 'qw', 'xz', 'jp', 'fj']
        if bigram in difficult_bigrams or char in 'qxz':
            char_modifier *= random.uniform(1.2, 1.5)
    
    # Enhanced typing patterns with Gaussian influence
    pattern_roll = random.random()
    if pattern_roll < BURST_CHANCE:
        char_modifier *= random.uniform(0.2, 0.5)  # Fast burst
    elif pattern_roll < BURST_CHANCE + HESITATION_CHANCE:
        char_modifier *= random.uniform(2.0, 3.5)  # Hesitation
    elif pattern_roll < BURST_CHANCE + HESITATION_CHANCE + MICRO_PAUSE_CHANCE:
        char_modifier *= random.uniform(1.2, 1.8)  # Micro-pause
    
    # Apply all modifiers
    final_delay = base_delay * char_modifier * flow_modifier
    
    # Add small jitter
    jitter = random.uniform(-0.01, 0.01)
    final_delay = max(0.005, final_delay + jitter)
    
    return final_delay

def human_type_enhanced(text, base_wpm=DEFAULT_BASE_WPM):
    """Enhanced typing with position tracking and resume capability"""
    global typing_state, typing_position
    
    if not text:
        print("[WARNING] No text to type!")
        return
    
    # Clean the text before typing
    original_length = len(text)
    text = clean_clipboard_text_advanced(text)
    cleaned_length = len(text)
    
    if original_length != cleaned_length:
        print(f"[INFO] 🧹 Advanced cleaning: {original_length} → {cleaned_length} characters")
    
    print(f"[INFO] 🚀 Enhanced typing: {len(text)} characters from position {typing_position}")
    print(f"[INFO] ⚡ Target WPM: {base_wpm} (Gaussian distribution)")
    print(f"[INFO] 🎮 Controls: F8=Pause | F9=Resume/Start | F10=Stop")
    
    start_time = time.time()
    chars_typed = 0
    current_flow_state = get_typing_flow_state()
    flow_change_counter = 0
    prev_char = None
    
    print(f"[INFO] 🌊 Flow state: '{current_flow_state}'")
    
    # Start from current position
    for i in range(typing_position, len(text)):
        # Thread safety for position tracking
        with typing_lock:
            if typing_state == TYPING_STOPPED:
                print(f"\n[INFO] 🛑 Typing stopped at position {i}")
                break
            typing_position = i
        
        # Check for pause
        while typing_state == TYPING_PAUSED:
            time.sleep(0.1)
            
        char = text[i]
        
        # Change typing flow state occasionally
        flow_change_counter += 1
        if flow_change_counter > random.randint(12, 35):
            current_flow_state = get_typing_flow_state()
            flow_change_counter = 0
        
        # Handle special characters
        if char == '\n':
            pyautogui.press('enter')
        elif char == '\t':
            pyautogui.press('tab')
        elif char == '\r':
            continue
        else:
            # Enhanced typo simulation
            if random.random() < 0.006:  # 0.6% chance of typo
                wrong_chars = 'qwertyuiopasdfghjklzxcvbnm'
                if char.isalpha():
                    wrong_char = random.choice(wrong_chars)
                    pyautogui.write(wrong_char)
                    time.sleep(random.uniform(0.08, 0.25))  # Notice mistake
                    pyautogui.press('backspace')
                    time.sleep(random.uniform(0.03, 0.12))  # Correct
            
            pyautogui.write(char)
        
        chars_typed += 1
        
        # Enhanced delay calculation
        delay = calculate_char_delay_enhanced(base_wpm, char, i, len(text), current_flow_state, prev_char)
        time.sleep(delay)
        
        prev_char = char
        
        # Progress update every 40 characters
        if chars_typed % 40 == 0:
            elapsed_time = time.time() - start_time
            current_wpm = (chars_typed / 5) / (elapsed_time / 60) if elapsed_time > 0 else 0
            progress = (i / len(text)) * 100
            print(f"[PROGRESS] {progress:.1f}% | WPM: {current_wpm:.1f} | Flow: {current_flow_state}")
    
    # Completion handling
    if typing_state == TYPING_ACTIVE:
        elapsed_time = time.time() - start_time
        final_wpm = (chars_typed / 5) / (elapsed_time / 60) if elapsed_time > 0 else 0
        print(f"\n[SUCCESS] ✅ Completed typing {chars_typed} characters!")
        print(f"[STATS] ⏱️  Time: {elapsed_time:.1f}s | WPM: {final_wpm:.1f}")
        
        # Reset position for next run
        with typing_lock:
            typing_position = 0
    
    typing_state = TYPING_STOPPED

def start_typing_enhanced(custom_wpm=None):
    """Enhanced start function with position tracking"""
    global typing_state, typing_thread, typing_position
    
    if typing_state == TYPING_ACTIVE:
        print("[INFO] ⚠️  Already typing! Use F8 to pause or F10 to stop.")
        return
    
    # Get clipboard content
    try:
        text = pyperclip.paste()
    except Exception as e:
        print(f"[ERROR] ❌ Could not access clipboard: {e}")
        return
    
    # Validate clipboard content
    if not text or not text.strip():
        print("[WARNING] ⚠️  Clipboard is empty or contains only whitespace!")
        return
    
    # Clean and analyze text
    original_length = len(text)
    cleaned_text = clean_clipboard_text_advanced(text)
    
    if original_length != len(cleaned_text):
        print(f"[INFO] 🧹 Advanced cleaning: {original_length} → {len(cleaned_text)} characters")
    
    # Show analysis
    char_count = len(cleaned_text)
    line_count = cleaned_text.count('\n') + 1
    word_count = len(cleaned_text.split())
    
    with typing_lock:
        remaining_chars = char_count - typing_position
        remaining_words = len(' '.join(cleaned_text.split()[typing_position//5:]))
    
    print(f"\n[INFO] 📋 Enhanced typing analysis:")
    print(f"[INFO] 📊 Total: {char_count} chars, {word_count} words, {line_count} lines")
    print(f"[INFO] 📍 Position: {typing_position}/{char_count} ({remaining_chars} remaining)")
    
    # Calculate estimated time
    wpm = custom_wpm or DEFAULT_BASE_WPM
    estimated_time = (remaining_words / wpm) * 60 if remaining_words > 0 else 0
    print(f"[INFO] ⏱️  Estimated time: {estimated_time:.1f}s at {wpm} WPM")
    
    # Show preview from current position
    preview_start = max(0, typing_position - 20)
    preview_text = cleaned_text[preview_start:typing_position + 80]
    preview_clean = preview_text.replace('\n', '↵').replace('\t', '→')
    
    if typing_position > 0:
        marker_pos = min(20, typing_position - preview_start)
        preview_display = preview_clean[:marker_pos] + "⚡" + preview_clean[marker_pos:]
    else:
        preview_display = preview_clean
    
    print(f"[INFO] 👀 Preview: {preview_display[:100]}{'...' if len(preview_display) > 100 else ''}")
    
    # Countdown
    print(f"[INFO] ⏰ Starting in 3 seconds... Position your cursor!")
    for i in range(3, 0, -1):
        print(f"[INFO] ⏱️  {i}...")
        time.sleep(1)
    
    # Start typing
    typing_state = TYPING_ACTIVE
    typing_thread = threading.Thread(target=human_type_enhanced, args=(cleaned_text, wpm), daemon=True)
    typing_thread.start()

def pause_typing():
    """Pause typing"""
    global typing_state
    
    if typing_state == TYPING_ACTIVE:
        typing_state = TYPING_PAUSED
        print(f"\n[INFO] ⏸️  Typing PAUSED at position {typing_position}")
    else:
        print(f"[INFO] ⚠️  No active typing to pause.")

def stop_typing():
    """Stop typing and reset position"""
    global typing_state, typing_position
    
    if typing_state in [TYPING_ACTIVE, TYPING_PAUSED]:
        typing_state = TYPING_STOPPED
        print(f"\n[INFO] 🛑 Typing STOPPED at position {typing_position}")
        print("[INFO] 💡 Position preserved for resume")
    else:
        print(f"[INFO] ⚠️  No active typing to stop.")

def reset_position():
    """Reset typing position to beginning"""
    global typing_position
    
    with typing_lock:
        typing_position = 0
    print("[INFO] 🔄 Position reset to beginning")

def resume_or_start():
    """Resume if paused, or start new typing"""
    global typing_state
    
    if typing_state == TYPING_PAUSED:
        typing_state = TYPING_ACTIVE
        print(f"\n[INFO] ▶️  Typing RESUMED from position {typing_position}")
    else:
        start_typing_enhanced()

def test_accessibility_permissions():
    """Test if we have proper accessibility permissions via pynput"""
    try:
        from pynput import keyboard as pynput_keyboard

        result = [True]

        def on_press(key):
            listener.stop()

        try:
            listener = pynput_keyboard.Listener(on_press=on_press)
            listener.start()
            listener.join(timeout=0.05)
            if listener.is_alive():
                listener.stop()
        except Exception:
            result[0] = False

        return result[0]

    except ImportError:
        return False
    except Exception:
        return False

def start_typing_slow():
    """Start typing in slow mode (50 WPM)"""
    global DEFAULT_BASE_WPM
    DEFAULT_BASE_WPM = 50
    print(f"\n[INFO] 🐌 SLOW MODE: {DEFAULT_BASE_WPM} WPM")
    start_typing_enhanced()

def start_typing_normal():
    """Start typing in normal mode (85 WPM)"""
    global DEFAULT_BASE_WPM
    DEFAULT_BASE_WPM = 85
    print(f"\n[INFO] ⚡ NORMAL MODE: {DEFAULT_BASE_WPM} WPM")
    start_typing_enhanced()

def start_typing_fast():
    """Start typing in fast mode (120 WPM)"""
    global DEFAULT_BASE_WPM
    DEFAULT_BASE_WPM = 120
    print(f"\n[INFO] 🚀 FAST MODE: {DEFAULT_BASE_WPM} WPM")
    start_typing_enhanced()

def start_typing_custom_100():
    """Start typing at 100 WPM"""
    print(f"\n[INFO] 🎯 CUSTOM 100 WPM MODE")
    start_typing_enhanced(100)

def start_typing_custom_150():
    """Start typing at 150 WPM"""
    print(f"\n[INFO] 🎯 CUSTOM 150 WPM MODE")
    start_typing_enhanced(150)

def setup_hotkeys():
    """Setup enhanced hotkeys for typing control using pynput (macOS compatible)"""
    try:
        from pynput import keyboard as pynput_keyboard

        print("[INFO] 🔐 Testing accessibility permissions...")

        if not test_accessibility_permissions():
            print("[ERROR] ❌ Accessibility permissions required!")
            print("[INFO] 🔧 To enable hotkeys:")
            print("   1. System Settings > Privacy & Security > Accessibility")
            print("   2. Add Terminal (or Python) to the allowed apps")
            print("   3. Restart this program")
            return False

        # Map pynput Key objects to callbacks
        hotkey_map = {
            pynput_keyboard.Key.f1:  start_typing_slow,
            pynput_keyboard.Key.f2:  start_typing_normal,
            pynput_keyboard.Key.f3:  start_typing_fast,
            pynput_keyboard.Key.f4:  start_typing_custom_100,
            pynput_keyboard.Key.f5:  start_typing_custom_150,
            pynput_keyboard.Key.f8:  pause_typing,
            pynput_keyboard.Key.f9:  resume_or_start,
            pynput_keyboard.Key.f10: stop_typing,
        }

        def on_press(key):
            callback = hotkey_map.get(key)
            if callback:
                threading.Thread(target=callback, daemon=True).start()

        print("[INFO] 🎹 Registering enhanced hotkeys...")
        descriptions = [
            "F1 - Slow Mode (50 WPM)",
            "F2 - Normal Mode (85 WPM)",
            "F3 - Fast Mode (120 WPM)",
            "F4 - Custom 100 WPM",
            "F5 - Custom 150 WPM",
            "F8 - Pause",
            "F9 - Resume/General Start",
            "F10 - Stop",
        ]
        for desc in descriptions:
            print(f"[INFO] ✅ {desc}")

        print(f"\n[SUCCESS] 🎉 {len(descriptions)}/{len(descriptions)} hotkeys registered!")
        print("[INFO] 🎮 ENHANCED HOTKEY CONTROLS:")
        print("\n   📊 SPEED MODES:")
        print("   • F1 - 🐌 Slow Mode (50 WPM)")
        print("   • F2 - ⚡ Normal Mode (85 WPM)")
        print("   • F3 - 🚀 Fast Mode (120 WPM)")
        print("   • F4 - 🎯 Custom 100 WPM")
        print("   • F5 - 🎯 Custom 150 WPM")
        print("\n   🎮 PLAYBACK CONTROLS:")
        print("   • F8 - ⏸️  Pause typing")
        print("   • F9 - ▶️  Resume/General start")
        print("   • F10 - ⏹️  Stop typing")
        print("\n[INFO] 🚀 Press F1-F5 to start typing in different speed modes!")
        print("[INFO] 🛑 Press Ctrl+C to exit")

        with pynput_keyboard.Listener(on_press=on_press) as listener:
            try:
                listener.join()
            except KeyboardInterrupt:
                pass

        print("\n[INFO] 👋 Exiting AutoTyper...")
        return True

    except ImportError:
        print("[ERROR] 📦 pynput library not available.")
        print("[INFO] 💻 Install with: pip3 install pynput")
        return False
    except Exception as e:
        print(f"[ERROR] ⚠️  Hotkey setup failed: {e}")
        return False

def try_alternative_hotkeys():
    """Try alternative Ctrl+Shift hotkey combinations using pynput"""
    try:
        from pynput import keyboard as pynput_keyboard

        print("[INFO] 🔄 Trying alternative hotkey combinations...")

        # Track modifier state
        pressed = set()

        alt_map = {
            '1': start_typing_slow,
            '2': start_typing_normal,
            '3': start_typing_fast,
            '4': start_typing_custom_100,
            '5': start_typing_custom_150,
            '8': pause_typing,
            '9': resume_or_start,
            '0': stop_typing,
        }

        def on_press(key):
            pressed.add(key)
            ctrl = (pynput_keyboard.Key.ctrl_l in pressed or
                    pynput_keyboard.Key.ctrl_r in pressed or
                    pynput_keyboard.Key.ctrl in pressed)
            shift = (pynput_keyboard.Key.shift_l in pressed or
                     pynput_keyboard.Key.shift_r in pressed or
                     pynput_keyboard.Key.shift in pressed)
            if ctrl and shift:
                try:
                    ch = key.char
                    if ch in alt_map:
                        threading.Thread(target=alt_map[ch], daemon=True).start()
                except AttributeError:
                    pass

        def on_release(key):
            pressed.discard(key)

        descriptions = [
            "Ctrl+Shift+1 - Slow Mode (50 WPM)",
            "Ctrl+Shift+2 - Normal Mode (85 WPM)",
            "Ctrl+Shift+3 - Fast Mode (120 WPM)",
            "Ctrl+Shift+4 - Custom 100 WPM",
            "Ctrl+Shift+5 - Custom 150 WPM",
            "Ctrl+Shift+8 - Pause",
            "Ctrl+Shift+9 - Resume/Start",
            "Ctrl+Shift+0 - Stop",
        ]
        for desc in descriptions:
            print(f"[INFO] ✅ {desc}")

        print(f"\n[SUCCESS] 🎉 {len(descriptions)}/{len(descriptions)} alternative hotkeys registered!")
        print("[INFO] 🎮 ALTERNATIVE HOTKEY CONTROLS:")
        print("\n   📊 SPEED MODES:")
        print("   • Ctrl+Shift+1 - 🐌 Slow Mode (50 WPM)")
        print("   • Ctrl+Shift+2 - ⚡ Normal Mode (85 WPM)")
        print("   • Ctrl+Shift+3 - 🚀 Fast Mode (120 WPM)")
        print("   • Ctrl+Shift+4 - 🎯 Custom 100 WPM")
        print("   • Ctrl+Shift+5 - 🎯 Custom 150 WPM")
        print("\n   🎮 PLAYBACK CONTROLS:")
        print("   • Ctrl+Shift+8 - ⏸️  Pause typing")
        print("   • Ctrl+Shift+9 - ▶️  Resume/General start")
        print("   • Ctrl+Shift+0 - ⏹️  Stop typing")
        print("\n[INFO] 🚀 Press Ctrl+Shift+1-5 to start typing in different speeds!")
        print("[INFO] 🛑 Press Ctrl+C to exit")

        with pynput_keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
            try:
                listener.join()
            except KeyboardInterrupt:
                pass

        print("\n[INFO] 👋 Exiting AutoTyper...")
        return True

    except Exception as e:
        print(f"[ERROR] ⚠️  Alternative hotkey setup failed: {e}")
        return False

def show_status():
    """Redirect to enhanced version"""
    show_status_enhanced()

def manual_mode():
    """Redirect to enhanced version"""
    manual_mode_enhanced()

def show_status_enhanced():
    """Enhanced status display with position tracking"""
    state_names = {
        TYPING_STOPPED: "🔴 STOPPED",
        TYPING_ACTIVE: "🟢 ACTIVE", 
        TYPING_PAUSED: "🟡 PAUSED"
    }
    
    print(f"\n📊 ENHANCED STATUS: {state_names.get(typing_state, 'UNKNOWN')}")
    print(f"⚡ WPM: {DEFAULT_BASE_WPM} (Gaussian distribution)")
    print(f"📍 Position: {typing_position}")
    
    try:
        clip = pyperclip.paste()
        if clip and clip.strip():
            original_length = len(clip)
            cleaned_clip = clean_clipboard_text_advanced(clip)
            cleaned_length = len(cleaned_clip)
            
            char_count = cleaned_length
            word_count = len(cleaned_clip.split())
            line_count = cleaned_clip.count('\n') + 1
            
            remaining_chars = max(0, char_count - typing_position)
            progress_pct = (typing_position / char_count * 100) if char_count > 0 else 0
            
            print(f"📋 Clipboard: {char_count} chars, {word_count} words, {line_count} lines")
            print(f"📈 Progress: {progress_pct:.1f}% ({remaining_chars} chars remaining)")
            
            if original_length != cleaned_length:
                print(f"🧹 Will clean: {original_length} → {cleaned_length} characters")
            
            estimated_time = (remaining_chars / 5 / DEFAULT_BASE_WPM) * 60
            print(f"⏱️  Estimated time: {estimated_time:.1f}s")
            
            # Show preview around current position
            preview_start = max(0, typing_position - 15)
            preview_end = min(len(cleaned_clip), typing_position + 65)
            preview = cleaned_clip[preview_start:preview_end]
            preview = preview.replace('\n', '↵').replace('\t', '→')
            
            if typing_position > 0 and typing_position < len(cleaned_clip):
                marker_pos = typing_position - preview_start
                if marker_pos < len(preview):
                    preview = preview[:marker_pos] + "⚡" + preview[marker_pos:]
            
            print(f"👀 Preview: {preview[:80]}{'...' if len(preview) > 80 else ''}")
        else:
            print("📋 Clipboard: Empty")
    except Exception:
        print("📋 Clipboard: Unreadable")

def manual_mode_enhanced():
    """Enhanced manual mode with position controls"""
    global typing_state, DEFAULT_BASE_WPM
    
    print("\n" + "="*65)
    print("      📝 ENHANCED MANUAL MODE - Advanced Features")
    print("="*65)
    print("\n💡 ENHANCED FEATURES:")
    print("   • 🎯 Position tracking & resume capability")
    print("   • 🧹 Advanced text cleaning")
    print("   • 📊 Gaussian delay distribution")
    print("   • 🔄 Smart flow state transitions")
    print("\n⌨️  USAGE:")
    print("   1. 📋 Copy text to clipboard")
    print("   2. ⏎  Choose speed & start typing")
    print("   3. 🎯 Position cursor (3s countdown)")
    print("   4. ⚡ Resume from any position!")
    print(f"\n⚡ SPEED CONTROLS:")
    print("   • 1 = Slow (50 WPM) | 2 = Normal (85 WPM)")
    print("   • 3 = Fast (120 WPM) | 4 = Custom 100 WPM")
    print("   • 5 = Custom 150 WPM | [number] = Custom WPM")
    print("   • r = Reset position | Enter = Current speed")
    
    while True:
        try:
            show_status_enhanced()
            
            command = input("\n>>> [1-5/r/Enter/WPM]=Start | 'q'=Quit: ").strip().lower()
            
            if command in ['q', 'quit', 'exit']:
                break
            elif command == 'r' or command == 'reset':
                reset_position()
            elif command == '1':
                start_typing_slow()
            elif command == '2' or command == '':
                start_typing_normal()
            elif command == '3':
                start_typing_fast()
            elif command == '4':
                start_typing_custom_100()
            elif command == '5':
                start_typing_custom_150()
            elif command.isdigit():
                custom_wpm = int(command)
                if 10 <= custom_wpm <= 300:
                    print(f"[INFO] ⚡ Custom WPM: {custom_wpm}")
                    start_typing_enhanced(custom_wpm)
                else:
                    print("[ERROR] ❌ WPM must be between 10-300")
            else:
                print("[ERROR] ❌ Invalid command. Use 1-5, 'r', number, or Enter")
                
        except KeyboardInterrupt:
            print("\n\n🛑 Interrupted by user")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            continue
    
    print("\n👋 Thanks for using Enhanced AutoTyper!")

# Enhanced main function
def main():
    """Enhanced main function"""
    print("="*70)
    print("     🤖 AutoTyper v4.0 - Enhanced Edition with Position Tracking")
    print("="*70)
    print("[INFO] 🚀 Advanced clipboard auto-typer with resume capability")
    if HAS_NUMPY:
        print("[INFO] 📋 Gaussian delay distribution for natural typing")
    else:
        print("[INFO] 📋 Basic random delay distribution")
    print("[INFO] 🎯 Position tracking & advanced text cleaning")
    print("[INFO] 🍎 Optimized for macOS with enhanced features")
    
    # Show initial status
    show_status_enhanced()
    
    # Try to setup hotkeys with multiple fallback options
    print("\n[INFO] 🎹 Setting up enhanced hotkey controls...")
    
    if setup_hotkeys():
        print("[INFO] ✅ AutoTyper session completed.")
    elif try_alternative_hotkeys():
        print("[INFO] ✅ AutoTyper session completed with alternative hotkeys.")
    else:
        print("\n[INFO] 📝 Hotkey setup failed. Starting Enhanced Manual Mode...")
        print("[INFO] 🍎 Enhanced manual mode with position tracking!")
        manual_mode_enhanced()
    
    # Cleanup
    global typing_state
    typing_state = TYPING_STOPPED
    print("\n👋 Thanks for using Enhanced AutoTyper!")
    print("🍎 Tip: Grant accessibility permissions for hotkey mode")
    if not HAS_NUMPY:
        print("💡 Install NumPy for better typing realism: pip3 install numpy")

if __name__ == "__main__":
    main()
