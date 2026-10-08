FROM public.ecr.aws/lambda/python:3.14 AS builder

ARG LEPTONICA_VERSION=1.86.0
ARG TESSERACT_VERSION=5.5.1

RUN dnf install -y \
    gcc \
    gcc-c++ \
    make \
    cmake \
    automake \
    autoconf \
    libtool \
    pkgconf-pkg-config \
    git \
    wget \
    tar \
    gzip \
    ca-certificates \
    libpng-devel \
    libjpeg-turbo-devel \
    libtiff-devel \
    zlib-devel \
    && dnf clean all

WORKDIR /tmp

# Build Leptonica
RUN wget \
        https://github.com/DanBloomberg/leptonica/releases/download/${LEPTONICA_VERSION}/leptonica-${LEPTONICA_VERSION}.tar.gz \
    && tar xzf leptonica-${LEPTONICA_VERSION}.tar.gz \
    && cd leptonica-${LEPTONICA_VERSION} \
    && ./configure --prefix=/opt \
    && make -j"$(nproc)" \
    && make install

ENV PKG_CONFIG_PATH=/opt/lib/pkgconfig
ENV LD_LIBRARY_PATH=/opt/lib

# Build Tesseract
RUN wget \
        https://github.com/tesseract-ocr/tesseract/archive/refs/tags/${TESSERACT_VERSION}.tar.gz \
        -O tesseract-${TESSERACT_VERSION}.tar.gz \
    && tar xzf tesseract-${TESSERACT_VERSION}.tar.gz \
    && cd tesseract-${TESSERACT_VERSION} \
    && ./autogen.sh \
    && ./configure --prefix=/opt \
    && make -j"$(nproc)" \
    && make install

RUN strip --strip-unneeded /opt/bin/tesseract \
    /opt/lib/libtesseract.so.5.0.5 \
    /opt/lib/libleptonica.so.6.0.0

# Runtime libs the Lambda image lacks (installed here only via the -devel packages); /opt/lib is on its library path.
RUN for lib in libjpeg.so.62 libpng16.so.16 libtiff.so.5 libjbig.so.2.1 libwebp.so.7 libgomp.so.1; do cp -L /lib64/$lib /opt/lib/; done

# Add trained language data
COPY tessdata/eng.traineddata /opt/share/tessdata/

ENV TESSDATA_PREFIX=/opt/share/tessdata

# Verify the build before producing the layer
RUN /opt/bin/tesseract --version
RUN test -f /opt/share/tessdata/eng.traineddata