FROM kbase/sdkbase2:python
MAINTAINER KBase Developer
# -----------------------------------------
# In this section, you can install any system dependencies required
# to run your App.  For instance, you could place an apt-get update or
# install line here, a git checkout to download code, or run any other
# installation scripts.

# Prepare ENV variables
ENV GTDBTK_DATA_PATH=/data PATH=/miniconda/bin:${PATH}

# Install dependencies
RUN apt-get update && apt-get install -y build-essential cmake wget

RUN pip uninstall -y numpy

# VirMatcher specifically
RUN conda install mamba -c conda-forge
RUN mamba install -y python=3.6 prodigal hmmer pplacer fastani fasttree mash numpy tqdm minced blast trnascan-se r-here r-seqinr r-dplyr r-stringr r-data.table pandas biopython psutil -c conda-forge -c bioconda -c r
RUN mamba install -y pyparsing
RUN mamba install -y gtdbtk -c bioconda
RUN pip install dendropy

RUN git clone https://github.com/soedinglab/WIsH.git && cd WIsH && cmake . && make && chmod +x WIsH && cp WIsH /miniconda/bin/

# Finally, "install"
RUN echo "Force pull again"
RUN git clone https://bitbucket.org/MAVERICLab/virmatcher.git && cd virmatcher && pip install . --no-deps

# Clean up
RUN apt-get clean && conda clean -y --all
RUN apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# -----------------------------------------

COPY ./ /kb/module
RUN mkdir -p /kb/module/work
RUN chmod -R a+rw /kb/module

WORKDIR /kb/module

RUN make all

ENTRYPOINT [ "./scripts/entrypoint.sh" ]

CMD [ ]
