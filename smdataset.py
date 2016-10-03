import fnmatch
import json
json.encoder.FLOAT_REPR = lambda f: ('%.6f' % f)
import logging as smlog
import os
import sys
import traceback

from abstime import calc_note_abs_times
from parse import parse_sm_txt

_ATTR_REQUIRED = ['title', 'offset', 'bpms', 'notes']
def find_and_parse_sm_files(sm_dp, wildcard=''):
  songs = []
  for root, dirnames, filenames in os.walk(sm_dp):
    sm_names = fnmatch.filter(filenames, '*{}*.sm'.format(wildcard))
    for sm_name in sm_names:
      # open file
      sm_fp = os.path.join(root, sm_name)
      with open(sm_fp, 'r') as sm_f:
        sm_txt = sm_f.read()

      # parse file
      try:
        sm_attrs = parse_sm_txt(sm_txt)
      except ValueError as e:
        smlog.error('{} in\n{}'.format(e, sm_fp))
        continue
      except Exception as e:
        smlog.critical('Unhandled parse exception {}'.format(traceback.format_exc()))
        raise e

      # check required attrs
      try:
        for attr_name in _ATTR_REQUIRED:
          if attr_name not in sm_attrs:
            raise ValueError('Missing required attribute {}'.format(attr_name))
      except ValueError as e:
        smlog.error('{}'.format(e))
        continue

      # handle missing music
      if 'music' not in sm_attrs:
        music_names = []
        sm_prefix = os.path.splitext(sm_name)[0]

        # check directory files for reasonable substitutes
        for filename in filenames:
          prefix, ext = os.path.splitext(filename)
          if ext.lower()[1:] in ['mp3', 'ogg']:
            music_names.append(filename)

        try:
          # handle errors
          if len(music_names) == 0:
            raise ValueError('No music files found')
          elif len(music_names) == 1:
            sm_attrs['music'] = music_names[0]
          else:
            raise ValueError('Multiple music files {} found'.format(music_names))
        except ValueError as e:
          smlog.error('{}'.format(e))
          continue

      # attach absolute music path for convenience
      music_fp = os.path.join(root, sm_attrs['music'])
      songs.append((sm_fp, music_fp, sm_attrs))
  return songs

if __name__ == '__main__':
  (SM_DIR, DS_OUT_DIR) = sys.argv[1:3]
  OPTS = sys.argv[3:]
  GEN_PREVIEWS = 'genprevs' in OPTS
  if GEN_PREVIEWS:
    from preview import write_preview_wav

  sm_files = find_and_parse_sm_files(SM_DIR)
  avg_difficulty = 0.0
  num_charts = 0
  for sm_fp, music_fp, sm_attrs in sm_files:
    smname = os.path.split(os.path.split(sm_fp)[0])[1]
    packname = os.path.split(os.path.split(os.path.split(sm_fp)[0])[0])[1]
    out_dir = os.path.join(DS_OUT_DIR, packname)
    if not os.path.exists(out_dir):
      os.makedirs(out_dir)
    out_json_fp = os.path.join(out_dir, '{}.json'.format(smname))
    out_json = {
      'sm_fp': os.path.abspath(sm_fp),
      'music_fp': os.path.abspath(music_fp),
      'bpms': sm_attrs['bpms'],
      'charts': [],
    }
    bpms = sm_attrs['bpms']
    offset = sm_attrs['offset']

    for idx, sm_notes in enumerate(sm_attrs['notes']):
      notes_abs_times = calc_note_abs_times(offset, bpms, sm_notes[5])
      notes = {
        'type': sm_notes[0],
        'desc_or_author': sm_notes[1],
        'difficulty_coarse': sm_notes[2],
        'difficulty_fine': sm_notes[3],
        'notes': notes_abs_times,
      }
      out_json['charts'].append(notes)

      if GEN_PREVIEWS:
        out_wav_fp = os.path.abspath(os.path.join(out_dir, '{}_{}.wav'.format(smname, idx)))
        write_preview_wav(out_wav_fp, notes_abs_times)
        notes['preview_fp'] = out_wav_fp

      note_difficulty = sm_notes[3]
      avg_difficulty += float(note_difficulty)
      num_charts += 1

    with open(out_json_fp, 'w') as out_f:
      try:
        out_f.write(json.dumps(out_json))
      except UnicodeDecodeError:
        smlog.error('Unicode error in {}'.format(sm_fp))
        continue

    print 'Parsed {} - {}: {} charts'.format(packname, smname, len(out_json['charts']))
  print 'Parsed {} stepfiles, {} charts, average difficulty {}'.format(len(sm_files), num_charts, avg_difficulty / num_charts)
