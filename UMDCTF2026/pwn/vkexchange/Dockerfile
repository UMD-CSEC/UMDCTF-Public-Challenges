FROM debian:bookworm-slim@sha256:f9c6a2fd2ddbc23e336b6257a5245e31f996953ef06cd13a59fa0a1df2d5c252 AS build

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    glslang-tools \
    libvulkan-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /src
COPY . .
RUN make clean && make && strip ./vkexchange

FROM debian:bookworm-slim@sha256:f9c6a2fd2ddbc23e336b6257a5245e31f996953ef06cd13a59fa0a1df2d5c252 AS app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libvulkan1 \
    mesa-vulkan-drivers \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY --from=build /src/vkexchange ./vkexchange
COPY flag.txt ./flag.txt
RUN printf '%s\n' \
    '#!/bin/sh' \
    'export LIBGL_ALWAYS_SOFTWARE=1' \
    'export VK_ICD_FILENAMES=/usr/share/vulkan/icd.d/lvp_icd.x86_64.json' \
    'if [ -r /app/flag.txt ]; then export FLAG="$(cat /app/flag.txt)"; fi' \
    'exec /app/vkexchange' \
    > ./run \
    && chmod +x ./run ./vkexchange

FROM pwn.red/jail

COPY --from=app / /srv

ENV JAIL_PORT=1451 JAIL_MEM=512M JAIL_PID=50 JAIL_TIME=120
