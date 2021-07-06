'''
Script to convert ctm to json containing entries for word timing information,
word confidences and optionally add punctuation and/or speaker tags.

NOTE: If diarization is specified, the ctm must be in order and have 
speaker tags as the last field of each line. 

e.g. usage
    python ctm_to_json.py <in:ctm>

testing with:
    python ctm_to_json.py /home/felix/tmp/decode_with_diarization_wrapper/eNews_Channel_Africa_2018-06-27_06.00.ctm /home/felix/tmp/decode_with_diarization_wrapper/eNews_Channel_Africa_2018-06-27_06.00.json --punctuate=1 --primary_lang=eng --diarization=1
    python ctm_to_json.py /home/felix/tmp/decode_with_diarization_wrapper/tmp.ctm /home/felix/tmp/decode_with_diarization_wrapper/tmp.json --primary_lang=eng --punctuate=1 --use_bert=1 --diarization=0
'''

import sys
import os
import json
import argparse
import re

def punctuate_transcript(sentence_list, lang, use_bert, diarized):

    dir_punctuate = os.environ['HOME'] + '/saigen/tools/segmentation_and_capitalisation' 
    sys.path.insert(0, dir_punctuate)

    if lang == 'mul':
        lang = 'eng'
    else:
        pass
    
    if lang == 'eng' and use_bert == 1:
        from punctuate_normalised_text import punctuate_string_list
        punctuated_sentence_list = punctuate_string_list(sentence_list, capitalise=1, capitalise_oov=0, gpu=0)

    else:
        # lstm
        from segment_and_punctuate_normalised_text import punctuate_string_list
        punctuated_sentence_list = punctuate_string_list(lang, sentence_list, capitalise=1, capitalise_oov=0, gpu=0)

    return ' '.join(punctuated_sentence_list)


def normalize_text(text):
    words = re.split('[!?., ]', text)
    words = [w.strip().lower() for w in words if len(w.strip()) > 0]
    return ' '.join(words)


def replace_acronyms_json(json):
    
    # replace sequence of lowercase acronyms with captilaised one word (a n c -> ANC)
    acronyms = ['ANC', 'SAL', 'KZN', 'MPL']
    
    # replace in transcript
    text = json['transcript']
    norm_words = normalize_text(text).split()
    
    for acronym in acronyms:
        pattern = fr'(?i) {acronym[0].lower()}'
        for c in acronym[1:]:
            pattern += fr' {c.lower()}'
        pattern += r'([ ,.?])'

        replacement = fr' {acronym}\1'
        text = re.sub(pattern, replacement, text)
    json['transcript'] = text
    
    
    # replace in json (rough method remove to word at index if the normalise text matches)
    for i, w in enumerate(norm_words):
        for acronym in acronyms:
            if len(norm_words[i:]) >= len(acronym):

                if norm_words[i:i+len(acronym)] == list(acronym.lower()):

                    # get new end time and confidence and remove letters
                    conf = 0
                    for j in range(1,len(acronym),1):
                        end_time = json['words'][i+1]['endTime']
                        conf += json['words'][i+1]['confidence']
                        del json['words'][i+1]

                    # replace word
                    json['words'][i]['word'] = acronym
                    json['words'][i]['endTime'] = end_time
                    json['words'][i]['confidence'] = (conf + json['words'][i]['confidence']) / len(acronym)
                    break
                    
    return json


def _create_args():
    parser = argparse.ArgumentParser()

    # required positional arguments
    parser.add_argument("input_file", type=str, help="Input file (ctm format) to be converted to json.")
    parser.add_argument("output_file", type=str, help="Output file in json format.")

    # optional arguments
    parser.add_argument("--primary_lang", type=str, help="Languge of ctm file, needed for punctuation (eng|afr|zulu|sotho)", 
                        default='eng')
    parser.add_argument("--punctuate", type=int, help="Indicate whether transcript is to be punctuated.",
                        default=0)
    parser.add_argument("--use_bert", type=int, help="Use BERT to punctuate, improved performance but close to 100x more computation.",
                        default=1)
    parser.add_argument("--word_cofidence", type=int, help="Add confidences for each individual word.", \
                        default=1)
    parser.add_argument("--diarization", type=int, help="Add speaker tags for each individual word. \
                        Ctm is required to have the speaker as the last field per row.", \
                        default=0)

    return parser.parse_args()


if __name__ == "__main__":
    
    args = _create_args()

    ctm = [l.strip() for l in open(args.input_file, 'r', encoding="utf-8").readlines() if len(l) > 0]
    json_transcript = {}
    
    # -------------------------------------
    # punctuate transcript
    # -------------------------------------

    if args.punctuate == 1:
        
        if args.diarization and len(ctm[0].split()) >= 7:
            # use speaker turns as sentence boundaries
            sentence_list = []
            current_speaker = ctm[0].split()[6]
            words_speaker_turn = ''
            for line in ctm:
                
                word, speaker = line.split()[4], line.split()[6] 
                
                if current_speaker == speaker:
                    words_speaker_turn += " " + word
                else:
                    sentence_list.append(words_speaker_turn)
                    current_speaker = speaker
                    words_speaker_turn = word
                    
            # get last words
            if len(words_speaker_turn) > 0:
                sentence_list.append(words_speaker_turn)
                    
        else:
            # use the plain trascript if no speaker turns
            transcript_words = []
            for line in ctm:
                transcript_words.append(line.split()[4])
            sentence_list = [' '.join(transcript_words)]
            
        json_transcript["transcript"] = punctuate_transcript(sentence_list, args.primary_lang, args.use_bert, args.diarization)
        
    # # write result
    # output = open(f"{args.output_file}.tmp", "w", encoding='utf-8')
    # output.write(json_transcript["transcript"])
    # output.close()
    # -------------------------------------
    # convert ctm to json
    # -------------------------------------

    confidences = []
    transcript_words = []
    words = []

    for i, line in enumerate(ctm):
        line = line.split(' ')

        # words
        w = {}
        w["startTime"] = float(line[2]) 
        w["endTime"] = round(float(line[2]) + float(line[3]), 2)
        
        # use punctuated word if available
        if args.punctuate == 1:
            w["word"] = json_transcript["transcript"].split()[i]
        else:
            w["word"] = line[4]
        
        # confidence per word is not included in google's API but may be useful 
        if args.word_cofidence == 1:
            w["confidence"] = float(line[5])
        
        # speaker tags only if speakers 
        if args.diarization == 1:
            if len(line) >= 7:
                w["speaker"] = line[6].strip()
            
        words.append(w)
        confidences.append(float(line[5]))
        transcript_words.append(w["word"])

        
    # store transcript and average confidence
    json_transcript["confidence"] = sum(confidences) / len(confidences) 
    json_transcript["words"] = words
    
    if args.punctuate != 1:
        # dont overerite punctuated transcript
        json_transcript["transcript"] = ' '.join(transcript_words)
    else:
        json_transcript = replace_acronyms_json(json_transcript)


    # add nesting to comply with google api
    alternatives = {"alternatives": [json_transcript]}
    full_json = {"results": [alternatives]}
    

    with open(args.output_file, 'w', encoding="utf-8") as json_file:
        json.dump(full_json, json_file)

    # convert into json to inspect output
    #full_json = json.dumps(full_json, indent=4) 
    #print(full_json)

    #print(transcript["transcript"])
