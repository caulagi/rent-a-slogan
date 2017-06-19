.PHONY: server clean

server:
	python server/server.py

clean:
	find . -type f -name '*.py[co]' -delete
	find . -type d -name '__pycache__' -delete
	rm -rf .coverage .cache
