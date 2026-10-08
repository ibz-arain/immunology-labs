setup:
	pip install -r requirements.txt

pipeline:
	python load_data.py
	python cell_frequency.py
	python response_analysis.py
	python subset_analysis.py

dashboard:
	streamlit run dashboard.py
