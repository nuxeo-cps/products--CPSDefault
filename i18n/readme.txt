Tips for translators
====================

General i18n / l10n tips
------------------------

Look in ../doc/HOWTO.i18n

Spellchecking using aspell
--------------------------

Run:

  grep -v '#' XX.po | grep -v msgid | aspell -l --lang=XX | sort -u

where XX=fr, en, es, it, de...

Then look at output and fix errors...

