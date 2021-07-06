#!/bin/bash

# paths
dir_tools=$HOME/saigen/tools
dir_data=/tmp/data
dir_models=$HOME/models
dir_helper_scripts=$HOME/helper_scripts

# bash helper functions
. $dir_tools/bash/bash_helper_functions.sh
. $dir_tools/bash/parse_options.sh

echo "Running: $0 $@"

# parse parameters
BUCKET_NAME=$1
OBJECT_NAME=$2
OBJECT_PATH=$3
OBJECT_URL=$4
DEC_LANG=$5
SR=$6
NUM_CHAN=$7
NUM_SPK=$8
SAC=$9
DIA=${10}
CUSTOM_GRAPH=${11}
PRIV=${12}
BATCHED=${13}
USER_ID=${14}
JOB_ID=${15}
TAG=${16}
NUM_THREADS=${17}
FE_API_KEY=${18}
RETURN_URL=${19}

use_bert=0

# source environment and configure params
source $HOME/saigen/.env
if [ $TAG == "none" ]; then
 TAG=$(openssl rand -base64 20 | tr -dc A-Za-z0-9)
fi
if [ $JOB_ID == "none" ]; then
 JOB_ID=$TAG
fi
if [ $SR == "BB" ]; then
  SR=16000
fi
if [ $SR == "NB" ]; then
  SR=8000
fi

# download data to decode
# TODO - adapt this for batched decoding
mkdir -p $dir_data
if [ $OBJECT_URL != "none" ]; then
  curl -o $dir_data/$OBJECT_NAME $OBJECT_URL
  echo "INFO: Done downloading file via URL."
else
  aws s3 cp s3://${BUCKET_NAME}/${OBJECT_PATH} $dir_data/$OBJECT_NAME
  echo "INFO: Done downloading file from S3."
fi

# check if file is a valid audio file
if is_this_a_media_file $dir_data/$OBJECT_NAME; then
  echo "INFO: Audio file $OBJECT_NAME is valid."
  audio_file=$dir_data/$OBJECT_NAME
else
  echo "WARNING: Audio file $OBJECT_NAME is NOT valid. Exiting."
  # TODO - update dynamodb (log user and maybe even email)
  exit 101
fi

# get duration of audio file
#audio_dur=$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 $audio_file)

# configure model and graph from SR and LANG
if [ $SR == 8000 ]; then
  case $DEC_LANG in
    afr)
      model="nb_af_gen_v1.1"
      graph="graph_nb_af_gen_v1.1_gen_2019-10-24"
      ;;
    eng)
      model="nb_en-za_gen_v2.1"
      graph="graph_nb_en-za_gen_v2.1_gen_2020-03-06"
      ;;
    zul)
      model="nb_zu_gen_v2.1"
      graph="graph_nb_zu_gen_v2.1_gen_2020-03-06"
      ;;
    sto)
      model="nb_st_gen_v2.1"
      graph="graph_nb_st_gen_v2.1_gen_2020-03-06"
      ;;
    mul)
      model="nb_af-en-za-st-zu_gen_v2.1"
      graph="graph_nb_af-en-za-st-zu_gen_v2.1_gen_2020-03-05"
      ;;
    *)
      echo -n "Error: Unknown language specified."
      exit 101
      ;;
  esac
fi

if [ $SR == 16000 ]; then
  case $DEC_LANG in
    afr)
      model="bb_af_gen_v1.1"
      graph="graph_saebcn_2020-07-01"
      ;;
    eng)
      model="bb_en-za_gen_v2.1"
      graph="graph_bb_en-za_gen_v2.1_novus_2020-07-01"
      ;;
    *)
      echo -n "Error: Cannot use this language with broadband decoding."
      exit 101
      ;;
  esac
fi

if [ $CUSTOM_GRAPH == "PARL" ]; then
  # parliment graph
  model="bb_en-za_gen_v2.1"
  #graph="graph_bb_en-za_gen_v2.1_rsa_parliament_2020-11-09"
  graph="graph_bb_en-za_gen_v2.1_rsa_parliament_2021-04-18"
  use_bert=1
fi

echo "Model: $model"
echo "Graph: $graph"

#TODO -  update dynamoDB before decoding

# create work dir
# TODO - adjust for batched
dir_work=/tmp/$DEC_LANG/$TAG
mkdir -p $dir_work

# always check NUM_CHAN for overide
if [ $SR == 8000 ]; then
  NUM_CHAN=$(ffprobe -i $audio_file -show_streams -select_streams a:0 -v 0 | grep "channels=" | sed "s/channels=//g")
  if [ NUM_CHAN == 2 ]; then
    DIA='no'
  fi
fi

# decode audio
sucesfully_decoded=false
if [ $DIA == "yes" ]; then
  echo "decoding with diarization =================================!!!!!!!!!!!!!!!!!!!!!"
  # bash ~/saigen/tools/speech_recognition/decode_chain_callbi.sh --diarization 1 --sr $SR --num-channels $NUM_CHAN --num-threads $NUM_THREADS --tag $TAG --dir-work $dir_work $dir_models/$model $dir_models/$model/exp/chain_cleaned/tdnn1g_sp/$graph $audio_file && sucesfully_decoded=true 
  bash ~/saigen/tools/speech_recognition/decode_wav_with_diarization.sh --num_speakers $NUM_SPK --sr $SR --num-channels $NUM_CHAN --num-threads $NUM_THREADS --tag $TAG --dir-work $dir_work $dir_models/$model $dir_models/$model/exp/chain_cleaned/tdnn1g_sp/$graph $audio_file && sucesfully_decoded=true
else
  bash ~/saigen/tools/speech_recognition/decode_chain_callbi.sh --diarization 0 --sr $SR --num-channels $NUM_CHAN --num-threads $NUM_THREADS --tag $TAG --dir-work $dir_work $dir_models/$model $dir_models/$model/exp/chain_cleaned/tdnn1g_sp/$graph $audio_file && sucesfully_decoded=true 
  if [ $NUM_CHANNELS == "2" ]; then
    awk '{print $1}' $local_work/$tag.merged.ctm | awk -F"." '{print $NF}' | paste -d " " /tmp/$LANG/$TAG/$TAG.merged.ctm - > /tmp/$LANG/$TAG/$TAG.spk_tagged.ctm
  fi
fi

# what ctm to use
if ([ $DIA == "yes" ]) || ([ $SR == 8000 ] && [ -f $dir_work/$TAG/$TAG.spk_tagged.ctm ]); then
  # i am unsure if it's going in here
  echo "gets into this part of run decode================================================="
  ctm_in=$dir_work/$TAG/$TAG.spk_tagged.ctm
  dr=1
else
  ctm_in=$dir_work/$TAG/$TAG.merged.ctm
  dr=0
fi

# do punctuation and capitalization and convert ctm to json

if [ $sucesfully_decoded ] && [ $SAC == "yes" ]; then
  echo "INFO: Performing punctuation and capitalization"
  python3 $dir_helper_scripts/ctm_to_json.py --diarization=$dr --use_bert=$use_bert --punctuate=1 $ctm_in $dir_work/$TAG.json
else
  python3 $dir_helper_scripts/ctm_to_json.py --diarization=$dr --punctuate=0 $ctm_in $dir_work/$TAG.json
fi

# send .ctm and .json files to s3
# add tags
dest_path=decoded/$TAG.json
aws s3 cp $dir_work/$TAG.json s3://$BUCKET_NAME/$dest_path

# update dyndb

# run flask app
FE_API_KEY=$X_API_KEY
#FE_URL='https://saigen.ai/jobcomplete/'
#FE_URL=$RETURN_URL
echo "Sending response to $RETURN_URL"
python3 $dir_helper_scripts/http_post_app.py -s3_decoded_path="$dest_path" -decoded_file_path="$dir_work/$TAG.json" -user_id="$USER_ID" -job_id="$JOB_ID" -x_api_key="$FE_API_KEY" -front_end_url="$RETURN_URL"

echo "Info[`date`]: $(basename $0) done."
exit $?

