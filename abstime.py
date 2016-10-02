_EPSILON = 1e-6

def bpm_to_spb(bpm):
  return 60.0 / bpm

def calc_segment_lengths(bpms):
  assert len(bpms) > 0
  segment_lengths = []
  for i in xrange(len(bpms) - 1):
    spb = bpm_to_spb(bpms[i][1])
    segment_lengths.append(spb * (bpms[i + 1][0] - bpms[i][0]))
  return segment_lengths

def calc_abs_for_beat(offset, bpms, segment_lengths, beat):
  bpm_idx = 0
  while bpm_idx < len(bpms) and beat + _EPSILON > bpms[bpm_idx][0]:
    bpm_idx += 1

  full_segment_total = sum(segment_lengths[:bpm_idx - 1])
  partial_segment_spb = bpm_to_spb(bpms[bpm_idx - 1][1])
  partial_segment = partial_segment_spb * (beat - bpms[bpm_idx - 1][0])

  return full_segment_total + partial_segment - offset

def calc_note_abs_times(offset, bpms, note_data):
  segment_lengths = calc_segment_lengths(bpms)

  # copy bpms
  bpms = bpms[:]
  inc = None
  inc_prev = None
  time = offset

  # beat loop
  note_abs_times = []
  beat_times = []
  for measure_num, measure in enumerate(note_data):
    beat_num = measure_num * 4
    pulses = len(measure) / 4
    pulses_beats = [x / float(pulses) for x in xrange(beat_num * pulses, (beat_num + 4) * pulses, 1)]
    for beat, data in zip(pulses_beats, measure):
      beat_abs = calc_abs_for_beat(offset, bpms, segment_lengths, beat)
      note_abs_times.append((beat_abs, data))
      beat_times.append(beat_abs)

  #TODO: remove when stable
  assert sorted(beat_times) == beat_times

  return note_abs_times
