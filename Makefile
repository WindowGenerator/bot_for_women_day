SRC_DIR = ./src


start-dev: 
	echo 0
	

format:
	black $(SRC_DIR)

lint:
	black --check $(SRC_DIR)