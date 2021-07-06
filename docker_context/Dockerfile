FROM kaldi_light:dsac

# get initial apt dependencies
RUN apt-get update \
    && apt-get -y install --no-install-recommends \
	python3-pip \
	python3-dev \
	build-essential \
	libssl-dev \
	libffi-dev \
	python3-setuptools \
	python3.6 \
	tree \
	libngram-tools \
	curl \
	swig \
	perl \
	gawk \
	gfortran \
	openssl \
	libfst-tools \
	time \
	pandoc \
	dos2unix \
	mediainfo

# pip3 dependencies
RUN pip install numpy --user\
	&& pip3 install awscli \
   	numpy \
	Bio \
	sklearn \
	pandas \
	wave \
	argparse \
	lingua

# sequiter dependencies
RUN pip3 install numpy \
	&& pip3 install git+https://github.com/sequitur-g2p/sequitur-g2p@master

# allignment CPAN dependencies
RUN cpan Lingua::EN::Numbers \
	&& cpan install Switch \
	&& cpan install AFR::AfrNumbers

# Get dependencies for segmentation and capitilisation
RUN pip3 install --no-cache-dir torch==1.4.0 torchvision==0.5.0 \
  && pip3 install --no-cache-dir sentencepiece==0.1.85 \
  && pip3 install --no-cache-dir tf-sentencepiece==0.1.85 \
  && pip3 install --no-cache-dir transformers==2.5.1 \
  && pip3 install --no-cache-dir tensorflow==2.0.0a0 \
  && pip3 install --no-cache-dir nltk==3.4.5 \
  && pip3 install --no-cache-dir keras==2.3.1 \
  && pip3 install --no-cache-dir pytorch-pretrained-bert==0.6.2 \
  && pip3 install --no-cache-dir future \
  && pip3 install --no-cache-dir Cython==0.28.5 \
  && pip3 install --no-cache-dir seqtag_keras==1.0.5 \
  && python3 -c "import nltk; nltk.download('punkt');" \
  && pip3 install --no-cache-dir h5py==2.10.0 \
  && pip3 install --no-cache-dir stanza==1.1.1 \
  && python3 -c "import stanza; stanza.download('en');" \
  && rm /root/stanza_resources/en/default.zip

# diarization dependecies
RUN git clone https://github.com/Jamiroquai88/VBDiarization.git /root/VBDiarization && \
 cd /root/VBDiarization && pip3 install -r requirements.txt && python3 setup.py install
ENV KALDI_ROOT_PATH="/root/local/src/kaldi"

# ensure that home always points to root
RUN mkdir -p /root/local/src && \
     mkdir /root/home && ln -s /root /home/root

# saigen codebase and models
RUN mkdir -p /root/saigen && \
	mkdir -p /root/models
COPY saigen/ /root/saigen
RUN chmod -R a+x ~/saigen/tools/*

# helper functions
RUN mkdir -p /root/helper_scripts
COPY /helper_scripts/run_decode.sh /root/helper_scripts/run_decode.sh
COPY /helper_scripts/ctm_to_json.py /root/helper_scripts/ctm_to_json.py
COPY /helper_scripts/http_post_app.py /root/helper_scripts/http_post_app.py

# environment variable defaults
ENV X_API_KEY='XXX-XXX-XXX'
ENV FE_API_KEY='XXX-XXX-XXX'
ENV BUCKET_NAME='none'
ENV OBJECT_NAME='none'
ENV OBJECT_PATH='none'
ENV OBJECT_URL='none'
ENV DEC_LANG='eng'
ENV SR=8000
ENV NUM_CHAN=1
ENV NUM_SPK=1
ENV SAC='no'
ENV DIA='no'
ENV CUSTOM_GRAPH='none'
ENV PRIV='no'
ENV BATCHED='no'
ENV USER_ID='none'
ENV JOB_ID='none'
ENV TAG='none'
ENV NUM_THREADS=2
ENV RETURN_URL='https://saigendac.com/jobcomplete/'

# run entrypoint
ENTRYPOINT bash /root/helper_scripts/run_decode.sh \
		$BUCKET_NAME \
		$OBJECT_NAME \
		$OBJECT_PATH \
		$OBJECT_URL \
		$DEC_LANG \
		$SR \
		$NUM_CHAN \
		$NUM_SPK \
		$SAC \
		$DIA \
		$CUSTOM_GRAPH \
		$PRIV \
		$BATCHED \
		$USER_ID \
		$JOB_ID \
		$TAG \
		$NUM_THREADS \
		$FE_API_KEY \
		$RETURN_URL

