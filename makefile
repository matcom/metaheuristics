pdf: slides/01-intro/01-intro.pdf

slides/01-intro/01-intro.pdf: slides/01-intro/main.md
	cd slides/01-intro/ && pandoc -t beamer -o 01-intro.pdf main.md

entr:
	find *.md . | entr make pdf
