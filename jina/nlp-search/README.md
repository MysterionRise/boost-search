## How to run example

1. `pip install -r requirements.txt`
2. Download data set from - https://www.kaggle.com/therohk/urban-dictionary-words-dataset
3. `python prepare_data.py --input=/path/to/urban-dict.csv`
4. `python app.py index --num-docs=1000`
5. `python app.py query --text "hello in japanese"`

python app.py query --text "hello in japanese"
python app.py query --text "kash mony"
python app.py query --text "very cool"

