all : results.png

results.png : analyze_labnote_data.py ./data.pickle
	python3 $<

data.pickle : ./fetch_data_1.py
	python3 $< -u dilawars -p $(LABNOTE_PASSWORD)
