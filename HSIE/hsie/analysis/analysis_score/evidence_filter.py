def filter_by_speaker(evidences, speaker_id):
    return [e for e in evidences if e.speaker_id == speaker_id]