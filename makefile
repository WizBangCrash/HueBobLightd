# hueboblightd makefile



all:

release:
	pandoc -o README.rst README.md
	
clean:
	rm -rf HueBobLightd/__pycache__
	rm -rf __pycache__