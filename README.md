# smdataset
Extracts note events and downbeats from Stepmania step files for music information retrieval tasks.

# Introduction
[Stepmania](http://www.stepmania.com/) has the potential to be a high-quality source of data for music event detection tasks as timing of events is critical to the game experienced. There is an enormous amount of metadata available which is distributed alongside the actual audio. The game has an active community of human content creators making these event annotations manually. The game file format is not particularly convenient for MIR so this package links the annotations to absolute times in seconds and serializes this information as simple JSON files.

# Usage
Usage is simplistic for now. To use, grab some music/stepfiles from [Stepmania Online](http://stepmaniaonline.net/). These are standardized releases that the community is currently using and the popular packs typically have high-quality annotations. Recommended packs include:

* In The Groove X
* Dance Dance Revolution (Official Konami Steps)
* Community Keyboard Megapack - Volume X
* Keyboard Mega Pack X

Extract each of these to one songs directory. This directory should contain folders whose names are the names of a pack. These packs should contain folders whose names are the names of the songs in that pack. This structure is essential for the proper formatting of the output JSON directory.

The command to run the parsing is:

```
$ python smdataset.py <SONGS_DIR> <OUT_DIR> <OPTS>
```

Current options:

* `genprevs`: If specified, generates a wav metronome file for each chart that should sync up with the music

# Data
The script outputs one JSON file representing all of the charts for a given song. A single song can have many charts, where a chart is a list of timed note events of varying difficulty/game mode. The following attributes are available in this JSON file:

* `sm_fp`: Absolute filepath for the original `.sm` file this was derived from
* `music_fp`: Absolute filepath for the `.mp3` or `.ogg` file the `.sm` file describes
* `bpms`: List of `[Beat, BPM]` pairs
* `notes`: List of charts where each chart is an object containing the attrs:
  * `type`: Type of chart, such as `dance-single` or `dance-double`, indicating the game mode (one or two 4-arrow pads)
  * `desc_or_author`: A free-text field reserved for a description or author for the chart. Can be useful as a single author might have more consistent difficulty assignments
  * `difficulty_coarse`: An author-assigned coarse difficulty; one of `Beginner`, `Easy`, `Medium`, `Hard`, `Challenge`, `Edit`
  * `difficulty_fine`: An author-assigned fine-grain difficulty; a numerical value where lower is easier and higher is harder. There is no science here and the numbers are extremely subjective
  * `notes`: List of `[Time (s), Event]` pairs. The length of the event should be consistent per chart and indicates the number of arrows in the game mode. For each arrow, one of the following values should occur. There is very little data for some of the arrow types, so it's probably a good idea to ignore them or interpret them as normal notes.
    * `0` (common): No note
    * `1` (common): Normal note
    * `2` (uncommon):  Hold head
    * `3` (uncommon): Hold/roll tail
    * `4` (very uncommon): Roll head
    * `M` (very uncommon): Mine
    * `K` (rare): Automatic keysound
    * `L` (rare): Lift note
    * `F` (rare): Fake note
  * `preview_fp`: Path to the preview wav file generated for this chart for sanity checking the event timings (if `genprevs` specified) 
