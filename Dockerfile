FROM python:3

WORKDIR /usr/src/app
RUN mkdir AI_Players
RUN mkdir GUI
RUN mkdir Game
RUN mkdir imgs

COPY AI_Players/*.py ./AI_Players/
COPY Game/*.py ./Game
COPY GUI/graphics.py ./GUI/
COPY imgs/wood.jpg ./imgs/
COPY main.py openings_book.txt requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
RUN mkdir Saved_games

VOLUME /Saved_games
ENV DISPLAY=0

CMD [ "python", "main.py" ]