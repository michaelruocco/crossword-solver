FROM --platform=linux/amd64 public.ecr.aws/lambda/python:3.14

ARG OPENCV_VERSION=4.9.0

RUN dnf install -y \
    gcc \
    gcc-c++ \
    cmake \
    make \
    git \
    wget \
    unzip \
    pkg-config \
    libjpeg-turbo-devel \
    libpng-devel \
    libtiff-devel \
    && dnf clean all

WORKDIR /tmp

RUN wget -q \
    https://github.com/opencv/opencv/archive/refs/tags/${OPENCV_VERSION}.zip \
    -O opencv.zip \
    && unzip -q opencv.zip \
    && mv opencv-${OPENCV_VERSION} opencv

WORKDIR /tmp/opencv/build

RUN /var/lang/bin/python3 -m pip install --no-cache-dir numpy

RUN cmake .. \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_INSTALL_PREFIX=/opt \
    -DBUILD_SHARED_LIBS=ON \
    -DBUILD_LIST=core,imgproc,imgcodecs,python3 \
    -DBUILD_TESTS=OFF \
    -DBUILD_PERF_TESTS=OFF \
    -DBUILD_EXAMPLES=OFF \
    -DBUILD_opencv_apps=OFF \
    -DWITH_FFMPEG=OFF \
    -DWITH_GSTREAMER=OFF \
    -DWITH_GTK=OFF \
    -DWITH_QT=OFF \
    -DWITH_OPENGL=OFF \
    -DWITH_V4L=OFF \
    -DWITH_1394=OFF \
    -DWITH_TBB=OFF \
    -DWITH_IPP=OFF \
    -DWITH_OPENCL=OFF \
    -DWITH_CUDA=OFF \
    -DWITH_PROTOBUF=OFF \
    -DWITH_JPEG=ON \
    -DWITH_PNG=ON \
    -DWITH_TIFF=ON \
    -DPYTHON3_EXECUTABLE=/var/lang/bin/python3 \
    -DPYTHON3_INCLUDE_DIR=/var/lang/include/python3.14 \
    -DPYTHON3_LIBRARY=/var/lang/lib/libpython3.14.so \
    -DPYTHON3_PACKAGES_PATH=/opt/python

RUN cmake --build . --parallel 2 \
    && cmake --install .

RUN rm -rf \
    /opt/include \
    /opt/share \
    /opt/bin \
    /opt/lib64/cmake

# Runtime libs the Lambda image lacks (installed here only via the -devel packages); /opt/lib is on its library path.
RUN mkdir -p /opt/lib \
    && for lib in libjpeg.so.62 libpng16.so.16 libtiff.so.5 libjbig.so.2.1 libwebp.so.7; do cp -L /lib64/$lib /opt/lib/; done
