pdf: slides/01-intro/01-intro.pdf slides/02-local-search/02-local-search.pdf slides/03-evolutionary-search/03-evolutionary-search.pdf

slides/01-intro/01-intro.pdf: slides/01-intro/readme.md
	cd slides/01-intro/ && pandoc -t beamer -o 01-intro.pdf readme.md

slides/02-local-search/02-local-search.pdf: slides/02-local-search/readme.md
	cd slides/02-local-search/ && pandoc -t beamer -o 02-local-search.pdf readme.md

slides/03-evolutionary-search/03-evolutionary-search.pdf: slides/03-evolutionary-search/readme.md
	cd slides/03-evolutionary-search/ && pandoc -t beamer -o 03-evolutionary-search.pdf readme.md

entr:
	find *.md . | entr make pdf
