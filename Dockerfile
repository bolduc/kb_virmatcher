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

# VirMatcher specifically
# conda install -c bioconda -c conda-forge minced blast trnascan-se r-here r-seqinr r-dplyr r-data.table r-stringr pandas biopython psutil
RUN conda update -y conda  # May be related to memory growth problems https://github.com/conda/conda/issues/5003
RUN conda install -y 'python=3.6'  # Update and version force
RUN conda install -y charset-normalizer -c conda-forge  # This has some sort of conflict/error
RUN conda install -y mamba -n base -c conda-forge  # 'conda<4.8' ???
RUN mamba install -y -q prodigal hmmer pplacer 'fastani=<1.32' fasttree mash numpy tqdm minced blast trnascan-se r-here r-seqinr r-dplyr r-stringr r-data.table pandas biopython psutil pyparsing -c conda-forge -c bioconda -c r
RUN mamba install -y -q 'gtdbtk<1.4.2' 'fastani=<1.32' -c bioconda
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
