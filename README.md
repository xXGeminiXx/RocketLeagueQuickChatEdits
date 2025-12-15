# DS5 Quickchats for Rocket League

A fun controller macro script that sends randomized, funny quickchat messages in Rocket League using D-pad combos on a DualSense or DS4 controller.

**Features:**
- 16 different D-pad combos for different message types
- 200+ unique message variations (no boring repeats!)
- Shuffle-bag randomization (guaranteed variety when spamming)
- Message cooldown system (won't repeat the same message for 10 minutes)
- Toggle on/off with the PS button
- CAT FAX (the most important feature)

## Is This Bannable?

**No.** This script just types text into chat - exactly like you would with a keyboard. It doesn't read game memory, inject code, or modify game files. It's the same as using a chat macro on a gaming keyboard. Psyonix has never banned anyone for typing funny messages faster.

## Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Connect your controller

USB or Bluetooth - either works.

### 3. Run the script

```bash
python DS5QuickchatsRL.py
```

> **Important:** Run this from Windows Python (PowerShell/CMD), not WSL. The script needs to type into whatever window has focus, and WSL can't reach Windows apps.

### 4. Play Rocket League

Make sure Rocket League is the focused window, then use D-pad combos to send messages!

## D-Pad Combos

Press two D-pad directions in sequence (within ~1 second) to trigger a message:

| Combo | Category | Example Message |
|-------|----------|-----------------|
| UP + UP | I Got It | "I got it! (Narrator: He did not.)" |
| UP + DOWN | Defending | "Defending! I am the wall. A very porous wall." |
| UP + LEFT | Need Boost | "Need boost! I'm running on hopes and fumes!" |
| UP + RIGHT | Confidence | "We're the main characters. Act like it!" |
| DOWN + UP | Greeting | "Hello! I'm here to kick ball and chew boost. And I'm all out of boost." |
| DOWN + DOWN | Cat Facts | "CAT FAX: Cats have 32 muscles in each ear. They still won't hear 'rotate.'" |
| DOWN + LEFT | Apology | "Sorry! I saw a boost pad and blacked out." |
| DOWN + RIGHT | No Problem | "No problem! (It was absolutely your fault.)" |
| LEFT + UP | Nice One | "Nice shot! That was illegal in at least 12 states." |
| LEFT + DOWN | Celebration | "Peak Rocket League! Clip it! Send it to NASA!" |
| LEFT + LEFT | Compliment | "Legendary!" |
| LEFT + RIGHT | Thanks | "Thanks! You're my favorite random!" |
| RIGHT + UP | Centering | "Centering! (Narrator: He was not centering.)" |
| RIGHT + DOWN | Challenge | "1v1 me behind the boost pad." |
| RIGHT + LEFT | Compliment | "Chef's kiss!" |
| RIGHT + RIGHT | Taunt | "Nice try! That was almost a thing!" |

**PS Button** = Toggle macros on/off

## Command Line Options

```bash
# Use team chat instead of all-chat
python DS5QuickchatsRL.py --chat-mode team

# Test without actually typing (prints to console)
python DS5QuickchatsRL.py --dry-run

# List detected controllers
python DS5QuickchatsRL.py --list-devices

# Force ASCII-only output (if chat mangles special characters)
python DS5QuickchatsRL.py --ascii

# Save message history across restarts (prevents repeats between sessions)
python DS5QuickchatsRL.py --persist quickchat_state.json
```

## How to Add Your Own Messages

The script is designed to be easy to customize! Open `DS5QuickchatsRL.py` and look for the `variations` dictionary near the top.

### Adding to an existing category

Find the category you want to add to and add your message:

```python
"Nice One": [
    "Nice shot! Was that intentional? Either way, WOW!",
    "Nice one! That was cleaner than my room!",
    # Add your own here:
    "Your new message here!",
],
```

### Creating a new category

Add a new entry to the `variations` dictionary:

```python
"My Custom Category": [
    "First message variation",
    "Second message variation",
    "Third message variation",
    # Add at least 3 for good variety
],
```

Then assign it to a D-pad combo in the `MacroEngine._macros` dictionary:

```python
self._macros: Dict[Tuple[str, str], str] = {
    # ... existing macros ...
    ("left", "down"): "{My Custom Category}",  # Change an existing combo
}
```

### Template syntax

Messages support simple templating to mix categories:

```python
"Hello {friend}!"                    # Inserts random friend variation
"{compliment:lower}"                 # Lowercase modifier
"{Confidence Boost:upper}"           # UPPERCASE modifier
"Nice one, {friend:capitalize}!"     # Capitalize first letter
```

Available modifiers: `lower`, `upper`, `capitalize`, `title`

## Tips for Good Messages

- **Keep it under ~100 characters** - Rocket League chat has limits
- **Add at least 10-15 variations** per category for good variety
- **Mix genuine callouts with jokes** - variety is the spice of life
- **Test with `--dry-run`** before using in-game

## Troubleshooting

### "No controllers detected"
- Make sure your controller is connected (USB or Bluetooth)
- Try unplugging and reconnecting
- Run `python DS5QuickchatsRL.py --list-devices` to see what pygame detects

### Messages aren't appearing in-game
- Make sure Rocket League is the focused window
- Check that your chat key bindings match (default: T for all-chat, Y for team)
- If you rebound chat keys, edit `DEFAULT_CHAT_KEYS` in the script

### Running from WSL doesn't work
- That's expected! WSL can't send keystrokes to Windows apps
- Run from Windows Python instead (PowerShell or CMD)

### Messages have weird characters
- Use `--ascii` flag to force ASCII-only output

## Contributing

Found a bug? Have a funny message idea? PRs welcome!

1. Fork the repo
2. Add your changes
3. Test with `--dry-run`
4. Submit a PR

**Message guidelines:**
- Keep it fun and Rocket League themed
- Nothing toxic - this is for friendly banter
- The funnier the better

## License

MIT License - Do whatever you want with it, just have fun in ranked.

## Credits

Made with chaos and caffeine. CAT FAX are the most important feature and this is not up for debate.
