# Explanation of the data files

Databases:

* AVEC is the AVEC2012 database at word level
* utt-AVEC is the AVEC2012 database down-sampled to the utterance level
* IEMOCAP is the IEMOCAP database (utterance-level)

Format of the .csv files:

* In emo files, the columns are {Arousal, Expectancy, Power, Valence} for utt-AVEC and AVEC, {Arousal, Power, Valence} for IEMOCAP. Original continuous annotations on each emotion dimension are grouped into three categories: {low, medium, high}
* In DIS-NV files, the columns are {FilledPause, Filler, Stutter, Laughter, AudibleBreath}
* In exDN files, the columns are {FilledPause, Filler, Stutter, Laughter, AudibleBreath, SpeechCorrection, TurnTakingTime, Prolongation}
* In GP files, the columns are {log-pitch, loudness, HF500}
* In GP+DN files, the columns are {log-pitch, loudness, HF500, FilledPause, Filler, Stutter, Laughter, AudibleBreath}
