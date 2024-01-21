FROM python:3.9-slim

WORKDIR /app

ARG TORCH_VERSION \
    TORCH_EXTRA_ARG \
    TORCH_EXTRA_URL

# 根據 .env 檔設定PyTorch安裝的版本。
# 如果有設定版本，則加入兩個等號，使其符合 pip install 的指令格式
RUN if [ -n "$TORCH_VERSION" ] ; \
    then \
        TORCH_VERSION="==${TORCH_VERSION}"; \
    fi; \
    pip3 install torch${TORCH_VERSION} ${TORCH_EXTRA_ARG} ${TORCH_EXTRA_URL}

# Install pytorch ROCm version

COPY ./requirements.txt ./requirements.txt

RUN pip install --no-cache-dir --user -r ./requirements.txt 

COPY . ./

CMD ["python", "news_server.py"]
EXPOSE 25505
