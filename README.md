# DS5 / DualSense Rocket League Quickchats

This script listens for **D-pad sequences** on a PlayStation controller (DualSense/DS4) and types fun custom “quick chats” into Rocket League using `pyautogui`.

## Install

```bash
python -m pip install -r requirements.txt
```

## Use

1. Connect your controller (USB or Bluetooth).
2. Start Rocket League.
3. Make sure Rocket League is the **focused window** (the script types into whatever has focus).
4. Run:

```bash
python DS5QuickchatsRL.py
```

Optional:

- List controllers detected by pygame:

```bash
python DS5QuickchatsRL.py --list-devices
```

- Force ASCII-only output (helps if chat mangles smart quotes/dashes):

```bash
python DS5QuickchatsRL.py --ascii
```

- Persist cooldown history across restarts (optional):

```bash
python DS5QuickchatsRL.py --persist quickchat_state.json
```

- Print messages instead of typing them:

```bash
python DS5QuickchatsRL.py --dry-run
```

## Controls

- **PS button** toggles macros on/off.
- Use **D-pad sequences** (press one direction then another within ~1.1s):

| Sequence | Message |
|---|---|
| Up → Up | `I got it{affirmation}` |
| Up → Down | `Defending...{affirmation}` |
| Down → Up | `OH SNAP! Hey there, {friend}` |
| Left → Up | `Nice shot!... {compliment}` |
| Right → Up | `Centering!... {foe}` |
| Left → Right | `Thanks!... {friend}` |
| Left → Down | `HA! {Celebration}` |
| Left → Left | `{compliment}` |
| Up → Right | `{Confidence Boost}` |
| Up → Left | `Need boost!... {friend}` |
| Down → Right | `No problem... {foe}` |
| Down → Left | `{Apology}` |
| Right → Left | `{compliment}` |
| Right → Right | `{Encouraging Taunt}` |
| Right → Down | `{Challenge}` |
| Down → Down | `{cat fact}` (CAT FAX) |

## Customize

- Edit `variations` in `DS5QuickchatsRL.py` to add/remove phrases.
- Edit `MacroEngine._macros` in `DS5QuickchatsRL.py` to change sequences and messages.
- Messages support simple templating:
  - `{friend}` inserts a random entry from the `"friend"` list.
  - `{compliment:lower}` applies a modifier (`lower`, `upper`, `capitalize`, `title`).
  - Variation keys are forgiving: `{Confidence_Boost}` and `{confidence boost}` both work.

## Notes / Safety

- `pyautogui` has a default fail-safe: moving your mouse to the top-left corner raises an exception to stop automation.
- If you run this from **WSL**, it will not be able to type into Windows Rocket League. Use Windows Python (PowerShell/CMD) instead.
