###############################################################################
# PV-Hawk  —  Raad Labs fork
#
# CUDA 11.8 / cuDNN 8 / Python 3.10 / TensorFlow 2.14
# Works on RTX 40X0 (sm_89 Ada Lovelace) GPUs.
# Python 3.10 chosen so the vendored pybind11 in g2opy and OpenSfM compiles
# without patching (PyFrameObject became opaque in 3.11).
###############################################################################

FROM nvidia/cuda:11.8.0-cudnn8-devel-ubuntu22.04

WORKDIR /

ARG DEBIAN_FRONTEND=noninteractive

# ── Core build tools, Python 3.10, OpenCV / matplotlib deps ─────────────
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        cmake \
        git \
        curl \
        pkg-config \
        python3 \
        python3-dev \
        python3-pip \
        python3-tk \
        libsm6 \
        libxext6 \
        libxrender-dev \
        libgl1-mesa-dev \
        libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# ── Python packages ──────────────────────────────────────────────────────
COPY requirements.txt /
RUN pip3 install --upgrade pip && \
    pip3 install tensorflow==2.14.0 && \
    pip3 install -r /requirements.txt


###############################################################################
#
#          OpenSfM dependencies (Eigen, glog, OpenCV, SuiteSparse, Ceres)
#
###############################################################################

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        libeigen3-dev \
        libgoogle-glog-dev \
        libopencv-dev \
        libsuitesparse-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Ceres 2 (disable TBB — tbb_stddef.h moved to oneapi/tbb on Ubuntu 22.04)
RUN mkdir -p /source && cd /source && \
    curl -L http://ceres-solver.org/ceres-solver-2.0.0.tar.gz | tar xz && \
    cd /source/ceres-solver-2.0.0 && \
    mkdir -p build && cd build && \
    cmake .. -DCMAKE_C_FLAGS=-fPIC -DCMAKE_CXX_FLAGS=-fPIC \
             -DBUILD_EXAMPLES=OFF -DBUILD_TESTING=OFF \
             -DCMAKE_DISABLE_FIND_PACKAGE_TBB=ON && \
    make -j4 install && \
    cd / && rm -rf /source/ceres-solver-2.0.0


###############################################################################
#
#   pyg2o graph optimizer
#
###############################################################################

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        qtdeclarative5-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /code
RUN git clone https://github.com/lukasbommes-forked-projects/g2opy.git

WORKDIR /code/g2opy/build
RUN cmake .. \
    && make -j12 \
    && make install -j12 \
    && ldconfig

WORKDIR /code/g2opy/
RUN python3 setup.py install


###############################################################################
#
#                          Setup OpenSfM
#
###############################################################################

COPY ./extractor/mapping/OpenSfM /pvextractor/extractor/mapping/OpenSfM

WORKDIR /pvextractor/extractor/mapping/OpenSfM
RUN python3 setup.py build
WORKDIR /pvextractor


###############################################################################
#
#                          Setup Mask R-CNN
#
###############################################################################

COPY ./extractor/segmentation/Mask_RCNN /pvextractor/extractor/segmentation/Mask_RCNN

WORKDIR /pvextractor/extractor/segmentation/Mask_RCNN
RUN pip3 install -e .
WORKDIR /pvextractor

ENV NVIDIA_VISIBLE_DEVICES=${NVIDIA_VISIBLE_DEVICES:-all}
ENV NVIDIA_DRIVER_CAPABILITIES=${NVIDIA_DRIVER_CAPABILITIES:+$NVIDIA_DRIVER_CAPABILITIES,}graphics
