FROM python:3.11-slim

WORKDIR /work

RUN pip install --no-cache-dir -i https://pypi.tuna.tsinghua.edu.cn/simple pytest

CMD ["python"]