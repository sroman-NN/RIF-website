# Atari 2600 TIA Sound utilities (Placeholders)

def get_atari_sound_registers():
    """Returns minimum TIA sound register offsets for Atari 2600.
    
    Exposed as a placeholder since RIF's focus for sound is GBA.
    """
    return {
        "AUDC0": 0x15, # Audio Control Channel 0
        "AUDC1": 0x16, # Audio Control Channel 1
        "AUDF0": 0x17, # Audio Frequency Channel 0
        "AUDF1": 0x18, # Audio Frequency Channel 1
        "AUDV0": 0x19, # Audio Volume Channel 0
        "AUDV1": 0x1A, # Audio Volume Channel 1
    }
