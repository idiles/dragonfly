clean:
	 for f in `find . -iname '*.pyc'`; do rm -f $$f; done
	 for f in `find . -iname '*.pyo'`; do rm -f $$f; done
	 for f in `find . -name '*~'`; do rm -f $$f; done
	 for f in `find . -name '.svn'`; do rm -rf $$f; done

stat:
	(for f in `find . -iname '*.py' -o -iname '*.kid' -o -iname '*.cfg'`; do svn blame $$f; done )| awk '{a[$$2] += 1;}; END {for (n in a) print n " " a[n]}'

test:
	nosetests --stop --with-doctest --exclude=testing .
