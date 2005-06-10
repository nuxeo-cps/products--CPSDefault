HTMLDOCS := howto-virtual_hosts.html guidelines-user_interface.html howto-search.html

all: $(HTMLDOCS)

%.html: %.txt
	/usr/share/python-docutils/rst2html.py -t --stylesheet-path=nuxeo_doc.css $< $@


%.toc: %.txt
	grep -B1 -e "==" $<  | grep -v "==" | grep -v "\-\-" |  sed "s/^\(.*\)/* \`\1\`_/g"


clean:
	rm -f *~
	rm -f $(HTMLDOCS)

