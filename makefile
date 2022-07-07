# Need to specify bash in order for conda activate to work.
SHELL=/bin/bash
# Note that the extra activate is needed to ensure that the activate floats env to the front of PATH
CONDA_ACTIVATE=source $$(conda info --base)/etc/profile.d/conda.sh ; conda activate ; conda activate

.PHONY: data_clearning
data_clearning:
	$(CONDA_ACTIVATE) p-poteka && python dataset/data-clearning/extract-data.py \
	&& python dataset/data-clearning/data-imputation.py \
	&& python dataset/data-clearning/accumurate-raf.py

test: test.py
	$(CONDA_ACTIVATE) p-poteka && python test.py

preprocess_pressure_data: dataset/data-making/make_PRS_SLP_image.py
	$(CONDA_ACTIVATE) p-poteka && python dataset/data-making/make_PRS_SLP_image.py \
		--data_root_path=../data \
		--target=prs \
		--n_jobs=10

preprocess_slp_data: dataset/data-making/make_PRS_SLP_image.py
	$(CONDA_ACTIVATE) p-poteka && python dataset/data-making/make_PRS_SLP_image.py \
		--data_root_path=../data \
		--target=slp \
		--n_jobs=10

preprocess_humidity_data: dataset/data-making/make_humidity_image.py
	$(CONDA_ACTIVATE) p-poteka && python dataset/data-making/make_humidity_image.py \
	--data_root_path=../data \
	--n_jobs=10

preprocess_temp_data: dataset/data-making/make_temp_image.py
	$(CONDA_ACTIVATE) p-poteka && python dataset/data-making/make_temp_image.py \
	--data_root_path=../data \
	--n_jobs=5

preprocess_wind_data: dataset/data-making/make_wind_image.py
	$(CONDA_ACTIVATE) p-poteka && python dataset/data-making/make_wind_image.py \
	--data_root_path=../data \
	--n_jobs=10 \
	--target=abs

preprocess_rain_data: dataset/data-making/make_rain_image.py
	$(CONDA_ACTIVATE) p-poteka && python dataset/data-making/make_rain_image.py \
	--data_root_path=../data \
	--n_jobs=10

extract_nexra_data: dataset/extracat-nexra-data/extract_nexra_data.py
	python dataset/extracat-nexra-data/extract_nexra_data.py \
	  --save_dir_path=/Users/akiranoda/Desktop/extract_nexra_data/ \
	  --n_cpus=5

visualize_nexra_data: dataset/visualize_nexra_data/main.py
	$(CONDA_ACTIVATE) p-poteka && python dataset/visualize_nexra_data/main.py \
	  --n_cpus=8

remove_files: remove_files.py
	$(CONDA_ACTIVATE) p-poteka && python remove_files.py